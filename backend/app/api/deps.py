from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models import Project, ProjectMember, User
from app.models.enums import ProjectMemberRole

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def get_project_member_or_403(project_id: str, db: Session, current_user: User) -> ProjectMember:
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id)
        .first()
    )
    if member:
        return member

    project = db.get(Project, project_id)
    if project and project.owner_id == current_user.id:
        owner_member = ProjectMember(
            project_id=project.id,
            user_id=current_user.id,
            role=ProjectMemberRole.owner,
            accepted_at=project.created_at,
        )
        db.add(owner_member)
        db.commit()
        db.refresh(owner_member)
        return owner_member

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this project")


def require_project_admin(project_id: str, db: Session, current_user: User) -> ProjectMember:
    member = get_project_member_or_403(project_id, db, current_user)
    if member.role not in {ProjectMemberRole.owner, ProjectMemberRole.admin}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return member
