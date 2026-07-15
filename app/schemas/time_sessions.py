from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TimeSessionResponse(BaseModel):
    id: UUID
    user_id: int
    project_id: UUID
    task_id: UUID | None
    start_time: datetime
    end_time: datetime | None
    total_seconds: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class TimeSessionCreate(BaseModel):
    user_id: int = Field(
        ge=1,
    )

    project_id: UUID

    task_id: UUID | None = None

    start_time: datetime

    end_time: datetime | None = None

    total_seconds: int = Field(
        default=0,
        ge=0,
    )


class TimeSessionUpdate(BaseModel):
    user_id: int = Field(
        ge=1,
    )

    project_id: UUID

    task_id: UUID | None = None

    start_time: datetime

    end_time: datetime | None = None

    total_seconds: int = Field(
        default=0,
        ge=0,
    )


class TimeSessionPatch(BaseModel):
    user_id: int | None = Field(
        default=None,
        ge=1,
    )

    project_id: UUID | None = None

    task_id: UUID | None = None

    start_time: datetime | None = None

    end_time: datetime | None = None

    total_seconds: int | None = Field(
        default=None,
        ge=0,
    )