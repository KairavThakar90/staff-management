from datetime import datetime, UTC
from pydantic import BaseModel, ConfigDict, Field


class TimeEntryActivityResponse(BaseModel):
    id: int
    organization_id: int
    time_entry_id: int
    recorded_at: datetime
    keyboard_strokes: int
    mouse_clicks: int
    mouse_movements: int
    activity_percentage: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeEntryActivityCreate(BaseModel):
    organization_id: int = Field(ge=1)
    time_entry_id: int = Field(ge=1)
    recorded_at: datetime | None = None
    keyboard_strokes: int = Field(default=0, ge=0)
    mouse_clicks: int = Field(default=0, ge=0)
    mouse_movements: int = Field(default=0, ge=0)
    activity_percentage: int = Field(default=0, ge=0, le=100)

    model_config = ConfigDict(extra="forbid")


class TimeEntryActivityUpdate(BaseModel):
    organization_id: int = Field(ge=1)
    time_entry_id: int = Field(ge=1)
    recorded_at: datetime | None = None
    keyboard_strokes: int = Field(default=0, ge=0)
    mouse_clicks: int = Field(default=0, ge=0)
    mouse_movements: int = Field(default=0, ge=0)
    activity_percentage: int = Field(default=0, ge=0, le=100)

    model_config = ConfigDict(extra="forbid")


class TimeEntryActivityPatch(BaseModel):
    organization_id: int | None = Field(default=None, ge=1)
    time_entry_id: int | None = Field(default=None, ge=1)
    recorded_at: datetime | None = None
    keyboard_strokes: int | None = Field(default=None, ge=0)
    mouse_clicks: int | None = Field(default=None, ge=0)
    mouse_movements: int | None = Field(default=None, ge=0)
    activity_percentage: int | None = Field(default=None, ge=0, le=100)

    model_config = ConfigDict(extra="forbid")
