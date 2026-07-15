from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums.time_entry_approval_status import TimeEntryApprovalStatus


class TimeEntryApprovalResponse(BaseModel):
    id: UUID
    manual_time_entry_id: UUID
    approved_by: int | None
    status: TimeEntryApprovalStatus
    remarks: str | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class TimeEntryApprovalCreate(BaseModel):
    manual_time_entry_id: UUID

    approved_by: int | None = Field(
        default=None,
        ge=1,
    )

    status: TimeEntryApprovalStatus = (
        TimeEntryApprovalStatus.pending
    )

    remarks: str | None = None

    approved_at: datetime | None = None


class TimeEntryApprovalUpdate(BaseModel):
    manual_time_entry_id: UUID

    approved_by: int | None = Field(
        default=None,
        ge=1,
    )

    status: TimeEntryApprovalStatus

    remarks: str | None = None

    approved_at: datetime | None = None


class TimeEntryApprovalPatch(BaseModel):
    manual_time_entry_id: UUID | None = None

    approved_by: int | None = Field(
        default=None,
        ge=1,
    )

    status: TimeEntryApprovalStatus | None = None

    remarks: str | None = None

    approved_at: datetime | None = None