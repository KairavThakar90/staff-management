from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    organization_id: int = Field(ge=1)
    user_id: int = Field(ge=1)
    project_id: int = Field(ge=1)
    task_id: int = Field(ge=1)
    start_time: datetime
    end_time: datetime | None = None
    total_seconds: int = Field(default=0, ge=0)
    status: TimeEntryStatus = TimeEntryStatus.running
    is_manual: bool = False
    is_billable: bool = True
    description: str | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_times(cls, values):
        if values.end_time is not None and values.end_time < values.start_time:
            raise ValueError("end_time must not be earlier than start_time")
        return values


class TimeEntryUpdate(BaseModel):
    organization_id: int = Field(ge=1)
    user_id: int = Field(ge=1)
    project_id: int = Field(ge=1)
    task_id: int = Field(ge=1)
    start_time: datetime
    end_time: datetime | None = None
    total_seconds: int = Field(default=0, ge=0)
    status: TimeEntryStatus = TimeEntryStatus.running
    is_manual: bool = False
    is_billable: bool = True
    description: str | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_times(cls, values):
        if values.end_time is not None and values.end_time < values.start_time:
            raise ValueError("end_time must not be earlier than start_time")
        return values


class TimeEntryPatch(BaseModel):
    organization_id: int | None = Field(default=None, ge=1)
    user_id: int | None = Field(default=None, ge=1)
    project_id: int | None = Field(default=None, ge=1)
    task_id: int | None = Field(default=None, ge=1)
    start_time: datetime | None = None
    end_time: datetime | None = None
    total_seconds: int | None = Field(default=None, ge=0)
    status: TimeEntryStatus | None = None
    is_manual: bool | None = None
    is_billable: bool | None = None
    description: str | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_times(cls, values):
        if values.start_time is not None and values.end_time is not None and values.end_time < values.start_time:
            raise ValueError("end_time must not be earlier than start_time")
        return values

#for start_time 
class TimeEntryStartRequest(BaseModel):
    organization_id: int
    user_id: int
    project_id: int
    task_id: int

#for stop_time
class TimeEntryStopRequest(BaseModel):
    organization_id: int
    user_id: int
    project_id: int
    task_id: int