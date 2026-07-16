from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums.time_entry_status import TimeEntryStatus


class TimeEntryResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    project_id: int
    task_id: int
    start_time: datetime
    end_time: datetime | None
    total_seconds: int
    status: TimeEntryStatus
    is_manual: bool
    is_billable: bool
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeEntryCreate(BaseModel):
    organization_id: int
    user_id: int
    project_id: int
    task_id: int
    start_time: datetime
    end_time: datetime | None = None
    total_seconds: int = 0
    status: TimeEntryStatus = TimeEntryStatus.running
    is_manual: bool = False
    is_billable: bool = True
    description: str | None = None


class TimeEntryUpdate(BaseModel):
    organization_id: int
    user_id: int
    project_id: int
    task_id: int
    start_time: datetime
    end_time: datetime | None = None
    total_seconds: int = 0
    status: TimeEntryStatus = TimeEntryStatus.running
    is_manual: bool = False
    is_billable: bool = True
    description: str | None = None


class TimeEntryPatch(BaseModel):
    organization_id: int | None = None
    user_id: int | None = None
    project_id: int | None = None
    task_id: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    total_seconds: int | None = None
    status: TimeEntryStatus | None = None
    is_manual: bool | None = None
    is_billable: bool | None = None
    description: str | None = None
