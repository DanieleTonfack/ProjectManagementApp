from enum import Enum


class ProjectVisibility(str, Enum):
    private = "private"
    team = "team"


class ProjectStatus(str, Enum):
    active = "active"
    archived = "archived"


class ProjectMemberRole(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class TaskStatus(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class NotificationType(str, Enum):
    task_assigned = "task_assigned"
    comment_received = "comment_received"
    status_changed = "status_changed"
    deadline_soon = "deadline_soon"
    project_invitation = "project_invitation"


class ActivityType(str, Enum):
    project_created = "project_created"
    project_updated = "project_updated"
    project_archived = "project_archived"
    member_invited = "member_invited"
    member_role_changed = "member_role_changed"
    member_removed = "member_removed"
    task_created = "task_created"
    task_updated = "task_updated"
    task_deleted = "task_deleted"
    task_status_changed = "task_status_changed"
    task_assigned = "task_assigned"
    comment_added = "comment_added"


class InvitationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"

