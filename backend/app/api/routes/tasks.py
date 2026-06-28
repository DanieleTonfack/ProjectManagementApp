from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_project_member_or_403, require_project_admin
from app.api.utils import create_notification, log_activity
from app.core.database import get_db
from app.models import Comment, Project, Task, User
from app.models.enums import ActivityType, NotificationType, TaskStatus
from app.schemas.task import TaskCommentCreate, TaskCreate, TaskUpdate

router = APIRouter(tags=["tasks"])


def serialize_task(task: Task, db: Session) -> dict:
    comment_count = db.query(Comment).filter(Comment.task_id == task.id).count()
    return {
        "id": task.id,
        "project_id": task.project_id,
        "assignee_id": task.assignee_id,
        "created_by_id": task.created_by_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date,
        "order_index": task.order_index,
        "comment_count": comment_count,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.get("/tasks/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    get_project_member_or_403(task.project_id, db, current_user)
    return serialize_task(task, db)


@router.get("/projects/{project_id}/tasks")
def list_project_tasks(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    get_project_member_or_403(project_id, db, current_user)
    tasks = db.query(Task).filter(Task.project_id == project_id).order_by(Task.order_index.asc(), Task.created_at.asc()).all()
    return [serialize_task(task, db) for task in tasks]


@router.post("/projects/{project_id}/tasks")
def create_task(
    project_id: str,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    get_project_member_or_403(project_id, db, current_user)

    task = Task(
        project_id=project_id,
        assignee_id=payload.assignee_id,
        created_by_id=current_user.id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        order_index=payload.order_index,
    )
    db.add(task)
    db.flush()

    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.task_created,
        title=f"Task '{task.title}' created",
        project_id=project.id,
        task_id=task.id,
    )

    if task.assignee_id:
        assignee = db.get(User, task.assignee_id)
        if assignee:
            create_notification(
                db,
                user_id=assignee.id,
                type=NotificationType.task_assigned,
                title=f"New task assigned in {project.name}",
                message=task.title,
                payload={"project_id": project.id, "task_id": task.id},
            )

    db.commit()
    db.refresh(task)
    return serialize_task(task, db)


@router.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    get_project_member_or_403(task.project_id, db, current_user)

    old_status = task.status
    old_assignee = task.assignee_id
    project = db.get(Project, task.project_id)

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.status is not None:
        task.status = payload.status
    if payload.priority is not None:
        task.priority = payload.priority
    if payload.assignee_id is not None:
        task.assignee_id = payload.assignee_id
    if payload.due_date is not None:
        task.due_date = payload.due_date
    if payload.order_index is not None:
        task.order_index = payload.order_index

    if task.status != old_status:
        log_activity(
            db,
            actor_id=current_user.id,
            type=ActivityType.task_status_changed,
            title=f"Task '{task.title}' moved to {task.status}",
            project_id=task.project_id,
            task_id=task.id,
            details={"from": old_status, "to": task.status},
        )

    if task.assignee_id and task.assignee_id != old_assignee:
        log_activity(
            db,
            actor_id=current_user.id,
            type=ActivityType.task_assigned,
            title=f"Task '{task.title}' assigned",
            project_id=task.project_id,
            task_id=task.id,
            details={"assignee_id": task.assignee_id},
        )
        assignee = db.get(User, task.assignee_id)
        if assignee and project:
            create_notification(
                db,
                user_id=assignee.id,
                type=NotificationType.task_assigned,
                title=f"Task assigned in {project.name}",
                message=task.title,
                payload={"project_id": project.id, "task_id": task.id},
            )

    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.task_updated,
        title=f"Task '{task.title}' updated",
        project_id=task.project_id,
        task_id=task.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return serialize_task(task, db)


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    require_project_admin(task.project_id, db, current_user)

    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.task_deleted,
        title=f"Task '{task.title}' deleted",
        project_id=task.project_id,
        task_id=task.id,
    )
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}


@router.get("/tasks/{task_id}/comments")
def list_comments(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    get_project_member_or_403(task.project_id, db, current_user)

    comments = db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at.asc()).all()
    return [
        {
            "id": comment.id,
            "task_id": comment.task_id,
            "author_id": comment.author_id,
            "content": comment.content,
            "created_at": comment.created_at,
        }
        for comment in comments
    ]


@router.post("/tasks/{task_id}/comments")
def add_comment(task_id: str, payload: TaskCommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    get_project_member_or_403(task.project_id, db, current_user)

    comment = Comment(task_id=task_id, author_id=current_user.id, content=payload.content)
    db.add(comment)
    log_activity(
        db,
        actor_id=current_user.id,
        type=ActivityType.comment_added,
        title=f"Comment added to '{task.title}'",
        project_id=task.project_id,
        task_id=task.id,
    )
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "task_id": comment.task_id,
        "author_id": comment.author_id,
        "content": comment.content,
        "created_at": comment.created_at,
    }
