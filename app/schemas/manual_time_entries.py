from datetime import datetime
import datetime as dt
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ManualTimeEntryResponse(BaseModel):
    id: UUID
    user_id: int
    project_id: UUID
    task_id: UUID | None
    date: dt.date | None = None
    start_time: datetime
    end_time: datetime
    total_seconds: int
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ManualTimeEntryCreate(BaseModel):
    user_id: int = Field(ge=1)
    project_id: UUID
    task_id: UUID | None = None
    date: dt.date
    start_time: datetime
    end_time: datetime
    total_seconds: int = Field(ge=0)
    description: str = Field(min_length=1)


class ManualTimeEntryUpdate(BaseModel):
    user_id: int = Field(ge=1)
    project_id: UUID
    task_id: UUID | None = None
    date: dt.date
    start_time: datetime
    end_time: datetime
    total_seconds: int = Field(ge=0)
    description: str = Field(min_length=1)


class ManualTimeEntryPatch(BaseModel):
    user_id: int | None = Field(default=None, ge=1)
    project_id: UUID | None = None
    task_id: UUID | None = None
    date: dt.date | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    total_seconds: int | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, min_length=1)