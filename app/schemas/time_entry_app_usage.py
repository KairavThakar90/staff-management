from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TimeEntryAppUsageResponse(BaseModel):
    id: int
    organization_id: int
    time_entry_id: int
    application_name: str
    window_title: str | None
    duration_seconds: int
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeEntryAppUsageSummaryResponse(BaseModel):
    application_name: str
    total_duration_seconds: int


class TimeEntryAppUsageOrganizationSummaryResponse(BaseModel):
    organization_id: int
    total_duration_seconds: int

class TimeEntryAppUsageCreate(BaseModel):
    organization_id: int = Field(ge=1)
    time_entry_id: int = Field(ge=1)
    application_name: str = Field(min_length=1, max_length=255)
    window_title: str | None = None
    duration_seconds: int = Field(default=0, ge=0)
    recorded_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class TimeEntryAppUsageUpdate(BaseModel):
    organization_id: int = Field(ge=1)
    time_entry_id: int = Field(ge=1)
    application_name: str = Field(min_length=1, max_length=255)
    window_title: str | None = None
    duration_seconds: int = Field(default=0, ge=0)
    recorded_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class TimeEntryAppUsagePatch(BaseModel):
    organization_id: int | None = Field(default=None, ge=1)
    time_entry_id: int | None = Field(default=None, ge=1)
    application_name: str | None = Field(default=None, min_length=1, max_length=255)
    window_title: str | None = None
    duration_seconds: int | None = Field(default=None, ge=0)
    recorded_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")
