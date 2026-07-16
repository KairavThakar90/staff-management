from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums.project_status import ProjectStatus


class ProjectResponse(BaseModel):
    id: int
    organization_id: int
    project_name: str
    description: str | None
    status: ProjectStatus
    start_date: date | None
    completed_at: datetime | None
    is_billable: bool
    time_tracked_seconds: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ProjectCreate(BaseModel):
    organization_id: int
    project_name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    status: ProjectStatus = ProjectStatus.planning
    start_date: date | None = None
    completed_at: datetime | None = None
    is_billable: bool = True
    time_tracked_seconds: int = 0
    created_by: int


class ProjectUpdate(BaseModel):
    organization_id: int
    project_name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    status: ProjectStatus = ProjectStatus.planning
    start_date: date | None = None
    completed_at: datetime | None = None
    is_billable: bool = True
    time_tracked_seconds: int = 0
    created_by: int


class ProjectPatch(BaseModel):
    organization_id: int | None = None
    project_name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    status: ProjectStatus | None = None
    start_date: date | None = None
    completed_at: datetime | None = None
    is_billable: bool | None = None
    time_tracked_seconds: int | None = None
    created_by: int | None = None
