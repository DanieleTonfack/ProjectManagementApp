from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProjectMemberRole, ProjectStatus, ProjectVisibility


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    visibility: ProjectVisibility = ProjectVisibility.private


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    visibility: ProjectVisibility | None = None
    status: ProjectStatus | None = None


class ProjectMemberUpdate(BaseModel):
    role: ProjectMemberRole


class ProjectInvite(BaseModel):
    email: str
    role: ProjectMemberRole = ProjectMemberRole.member
    message: str | None = None


class ProjectMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    user_id: str
    role: ProjectMemberRole
    accepted_at: datetime | None = None


class ProjectRead(BaseModel):
    id: str
    name: str
    description: str | None = None
    visibility: ProjectVisibility
    status: ProjectStatus
    owner_id: str
    created_at: datetime
    updated_at: datetime

