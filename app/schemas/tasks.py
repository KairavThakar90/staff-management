from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums.task_status import TaskStatus


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    parent_task_id: UUID | None
    assigned_to: int | None
    task_name: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    created_by: int | None
    deleted_at: datetime | None
    start_date: date | None
    due_date: date | None
    completed_at: datetime | None
    estimated_hours: Decimal | None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class TaskCreate(BaseModel):
    project_id: UUID

    assigned_to: int | None = None
    parent_task_id: UUID | None = None

    task_name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    status: TaskStatus = TaskStatus.todo

    created_by: int | None = None

    start_date: date | None = None

    due_date: date | None = None

    completed_at: datetime | None = None

    estimated_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )

    is_active: bool = True


class TaskUpdate(BaseModel):
    project_id: UUID

    assigned_to: int | None = None
    parent_task_id: UUID | None = None

    task_name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    status: TaskStatus = TaskStatus.todo

    created_by: int | None = None

    start_date: date | None = None

    due_date: date | None = None

    completed_at: datetime | None = None

    estimated_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )

    is_active: bool = True


class TaskPatch(BaseModel):
    project_id: UUID | None = None
    assigned_to: int | None = None
    parent_task_id: UUID | None = None

    task_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    status: TaskStatus | None = None

    created_by: int | None = None

    start_date: date | None = None

    due_date: date | None = None

    completed_at: datetime | None = None

    estimated_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )

    is_active: bool | None = None