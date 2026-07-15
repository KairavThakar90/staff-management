from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums.project_status import ProjectStatus


class ProjectResponse(BaseModel):
    id: UUID
    organization_id: UUID
    project_name: str
    description: str | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    start_date: date | None
    is_billable: bool
    is_active: bool
    created_by: int | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ProjectCreate(BaseModel):
    organization_id: UUID

    project_name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    status: ProjectStatus = ProjectStatus.planning

    created_by: int | None = None

    start_date: date | None = None

    is_billable: bool = True

    is_active: bool = True


class ProjectUpdate(BaseModel):
    organization_id: UUID

    project_name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    status: ProjectStatus = ProjectStatus.planning

    created_by: int | None = None

    start_date: date | None = None

    is_billable: bool = True

    is_active: bool = True


class ProjectPatch(BaseModel):
    organization_id: UUID | None = None

    project_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    status: ProjectStatus | None = None

    created_by: int | None = None

    start_date: date | None = None

    is_billable: bool | None = None

    is_active: bool | None = None