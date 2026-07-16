from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.enums.task_status import TaskStatus


class TaskResponse(BaseModel):
    id: int
    organization_id: int
    project_id: int
    task_name: str
    description: str | None
    status: TaskStatus
    start_date: date | None
    due_date: date | None
    estimated_hours: Decimal | None
    time_tracked_seconds: int
    completed_at: datetime | None
    completed_by: int | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    organization_id: int
    project_id: int
    task_name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    status: TaskStatus = TaskStatus.todo
    start_date: date | None = None
    due_date: date | None = None
    estimated_hours: Decimal | None = None
    time_tracked_seconds: int = 0
    completed_at: datetime | None = None
    completed_by: int | None = None
    created_by: int


class TaskUpdate(BaseModel):
    organization_id: int
    project_id: int
    task_name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    status: TaskStatus = TaskStatus.todo
    start_date: date | None = None
    due_date: date | None = None
    estimated_hours: Decimal | None = None
    time_tracked_seconds: int = 0
    completed_at: datetime | None = None
    completed_by: int | None = None
    created_by: int


class TaskPatch(BaseModel):
    organization_id: int | None = None
    project_id: int | None = None
    task_name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    status: TaskStatus | None = None
    start_date: date | None = None
    due_date: date | None = None
    estimated_hours: Decimal | None = None
    time_tracked_seconds: int | None = None
    completed_at: datetime | None = None
    completed_by: int | None = None
    created_by: int | None = None
