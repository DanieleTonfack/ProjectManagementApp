from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_project_member_or_403, require_project_admin
from app.api.utils import create_notification, log_activity
from app.core.database import get_db
from app.models import Invitation, Project, ProjectMember, Task, User
from app.models.enums import (
    ActivityType,
    InvitationStatus,
    NotificationType,
    ProjectMemberRole,
    ProjectStatus,
    ProjectVisibility,
    TaskStatus,
)
from app.schemas.project import ProjectCreate, ProjectInvite, ProjectMemberUpdate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


def project_accessible_query(db: Session, user_id: str):
    return (
        db.query(Project)
        .outerjoin(ProjectMember, and_(ProjectMember.project_id == Project.id, ProjectMember.user_id == user_id))
        .filter(or_(Project.owner_id == user_id, ProjectMember.id.isnot(None)))
        .distinct()
    )


def project_summary(db: Session, project: Project) -> dict:
    task_count = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
    todo_count = db.query(func.count(Task.id)).filter(Task.project_id == project.id, Task.status == TaskStatus.todo).scalar() or 0
    doing_count = db.query(func.count(Task.id)).filter(Task.project_id == project.id, Task.status == TaskStatus.doing).scalar() or 0
    done_count = db.query(func.count(Task.id)).filter(Task.project_id == project.id, Task.status == TaskStatus.done).scalar() or 0
    member_count = db.query(func.count(ProjectMember.id)).filter(ProjectMember.project_id == project.id).scalar() or 0
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "visibility": project.visibility,
        "status": project.status,
        "owner_id": project.owner_id,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "task_count": task_count,
        "member_count": member_count,
        "todo_count": todo_count,
        "doing_count": doing_count,
        "done_count": done_count,
    }


@router.get("")
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = project_accessible_query(db, current_user.id).order_by(Project.updated_at.desc()).all()
    return [project_summary(db, project) for project in projects]


@router.post("")
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        visibility=payload.visibility,
    )
    db.add(project)
    db.flush()
    membership = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role=ProjectMemberRole.owner,
        accepted_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.project_created,
        title=f"Project '{project.name}' created",
        project_id=project.id,
        details={"project_name": project.name},
    )
    db.commit()
    db.refresh(project)
    return project_summary(db, project)


@router.get("/{project_id}")
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    get_project_member_or_403(project_id, db, current_user)
    return project_summary(db, project)


@router.patch("/{project_id}")
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    require_project_admin(project_id, db, current_user)

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.visibility is not None:
        project.visibility = payload.visibility
    if payload.status is not None:
        project.status = payload.status
        if payload.status == ProjectStatus.archived:
            project.archived_at = datetime.now(timezone.utc)

    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.project_updated,
        title=f"Project '{project.name}' updated",
        project_id=project.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project_summary(db, project)


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    require_project_admin(project_id, db, current_user)

    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.project_archived,
        title=f"Project '{project.name}' deleted",
        project_id=project.id,
    )
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}


@router.get("/{project_id}/kanban")
def project_kanban(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    get_project_member_or_403(project_id, db, current_user)

    tasks = (
        db.query(Task)
        .filter(Task.project_id == project_id)
        .order_by(Task.order_index.asc(), Task.created_at.asc())
        .all()
    )
    columns = {status.value: [] for status in TaskStatus}
    for task in tasks:
        columns[task.status.value].append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "assignee_id": task.assignee_id,
                "due_date": task.due_date,
                "order_index": task.order_index,
            }
        )
    return {"project": project_summary(db, project), "columns": columns}


@router.get("/{project_id}/members")
def list_members(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    get_project_member_or_403(project_id, db, current_user)
    members = (
        db.query(ProjectMember, User)
        .join(User, User.id == ProjectMember.user_id)
        .filter(ProjectMember.project_id == project_id)
        .all()
    )
    return [
        {
            "id": member.id,
            "project_id": member.project_id,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": member.role,
            "accepted_at": member.accepted_at,
        }
        for member, user in members
    ]


@router.post("/{project_id}/members/invite")
def invite_member(
    project_id: str,
    payload: ProjectInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    require_project_admin(project_id, db, current_user)

    target_user = db.query(User).filter(User.email == payload.email).first()
    invitation = Invitation(
        project_id=project_id,
        email=payload.email,
        role=payload.role,
        token=str(uuid4()),
        invited_by_id=current_user.id,
        message=payload.message,
        status=InvitationStatus.pending,
    )
    db.add(invitation)

    if target_user:
        existing_member = (
            db.query(ProjectMember)
            .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == target_user.id)
            .first()
        )
        if existing_member is None:
            member = ProjectMember(
                project_id=project_id,
                user_id=target_user.id,
                role=payload.role,
                invited_by_id=current_user.id,
                accepted_at=datetime.now(timezone.utc),
            )
            db.add(member)
        invitation.status = InvitationStatus.accepted
        create_notification(
            db,
            user_id=target_user.id,
            type=NotificationType.project_invitation,
            title=f"Invitation to project {project.name}",
            message=payload.message or f"You were invited to join {project.name}",
            payload={"project_id": project.id, "role": payload.role},
        )

    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.member_invited,
        title=f"Member invited to {project.name}",
        project_id=project.id,
        details={"email": payload.email, "role": payload.role},
    )
    db.commit()
    db.refresh(invitation)
    return {
        "id": invitation.id,
        "project_id": invitation.project_id,
        "email": invitation.email,
        "role": invitation.role,
        "status": invitation.status,
        "token": invitation.token,
        "message": invitation.message,
    }


@router.patch("/{project_id}/members/{member_id}")
def update_member_role(
    project_id: str,
    member_id: str,
    payload: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    require_project_admin(project_id, db, current_user)

    member = db.get(ProjectMember, member_id)
    if member is None or member.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == ProjectMemberRole.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner role cannot be changed")

    member.role = payload.role
    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.member_role_changed,
        title=f"Role updated in {project.name}",
        project_id=project.id,
        details={"member_id": member.user_id, "role": payload.role},
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return {"id": member.id, "project_id": member.project_id, "user_id": member.user_id, "role": member.role}


@router.delete("/{project_id}/members/{member_id}")
def remove_member(
    project_id: str,
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    require_project_admin(project_id, db, current_user)

    member = db.get(ProjectMember, member_id)
    if member is None or member.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == ProjectMemberRole.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner cannot be removed")

    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.member_removed,
        title=f"Member removed from {project.name}",
        project_id=project.id,
        details={"member_id": member.user_id},
    )
    db.delete(member)
    db.commit()
    return {"detail": "Member removed"}

