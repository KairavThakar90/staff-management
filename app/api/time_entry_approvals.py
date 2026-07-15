from datetime import datetime, timezone
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.enums.time_entry_approval_status import TimeEntryApprovalStatus
from app.models.manual_time_entries import ManualTimeEntry
from app.models.time_entry_approvals import TimeEntryApproval
from app.schemas.time_entry_approvals import (
    TimeEntryApprovalCreate,
    TimeEntryApprovalPatch,
    TimeEntryApprovalResponse,
    TimeEntryApprovalUpdate,
)

router = APIRouter(
    prefix="/time-entry-approvals",
    tags=["Time Entry Approvals"],
)


def get_time_entry_approval_or_404(
    approval_id: UUID,
    db: Session,
) -> TimeEntryApproval:

    approval = db.scalar(
        select(TimeEntryApproval).where(
            TimeEntryApproval.id == approval_id
        )
    )

    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry approval not found.",
        )

    return approval


def handle_integrity_error(e: IntegrityError):
    """Translate known DB constraint violations into clean HTTP errors."""

    error = str(e.orig)

    if "uq_time_entry_approvals_manual_time_entry" in error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Approval already exists for this manual time entry.",
        )

    if "fk_time_entry_approvals_manual_time_entry" in error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manual time entry not found.",
        )

    if "chk_time_entry_approvals_approved_at" in error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="approved_at is required when status is not 'pending'.",
        )

    if "chk_time_entry_approvals_status" in error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid status value.",
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database error.",
    )


@router.get(
    "",
    response_model=list[TimeEntryApprovalResponse],
    summary="Get all time entry approvals",
)
def get_time_entry_approvals(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(TimeEntryApproval)
    ).all()


@router.get(
    "/{approval_id}",
    response_model=TimeEntryApprovalResponse,
    summary="Get time entry approval by ID",
)
def get_time_entry_approval(
    approval_id: UUID,
    db: Session = Depends(get_db),
):
    return get_time_entry_approval_or_404(
        approval_id,
        db,
    )


@router.post(
    "",
    response_model=TimeEntryApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create time entry approval",
)
def create_time_entry_approval(
    approval_data: TimeEntryApprovalCreate,
    db: Session = Depends(get_db),
):

    manual_entry = db.scalar(
        select(ManualTimeEntry).where(
            ManualTimeEntry.id == approval_data.manual_time_entry_id
        )
    )

    if manual_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manual time entry not found.",
        )

    approval_dict = approval_data.model_dump()

    # Auto-set approved_at if status is not pending and it wasn't provided
    if (
        approval_dict["status"] != TimeEntryApprovalStatus.pending
        and approval_dict["approved_at"] is None
    ):
        approval_dict["approved_at"] = datetime.now(timezone.utc)

    new_approval = TimeEntryApproval(**approval_dict)

    try:

        db.add(new_approval)
        db.commit()
        db.refresh(new_approval)

    except IntegrityError as e:

        db.rollback()
        handle_integrity_error(e)

    return new_approval


@router.put(
    "/{approval_id}",
    response_model=TimeEntryApprovalResponse,
    summary="Update time entry approval",
)
def update_time_entry_approval(
    approval_id: UUID,
    approval_data: TimeEntryApprovalUpdate,
    db: Session = Depends(get_db),
):

    approval = get_time_entry_approval_or_404(
        approval_id,
        db,
    )

    manual_entry = db.scalar(
        select(ManualTimeEntry).where(
            ManualTimeEntry.id == approval_data.manual_time_entry_id
        )
    )

    if manual_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manual time entry not found.",
        )

    update_data = approval_data.model_dump()

    # Auto-set approved_at if status is not pending and it wasn't provided
    if (
        update_data["status"] != TimeEntryApprovalStatus.pending
        and update_data["approved_at"] is None
    ):
        update_data["approved_at"] = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(approval, field, value)

    approval.updated_at = datetime.now(timezone.utc)

    try:

        db.commit()
        db.refresh(approval)

    except IntegrityError as e:

        db.rollback()
        handle_integrity_error(e)

    return approval


@router.patch(
    "/{approval_id}",
    response_model=TimeEntryApprovalResponse,
    summary="Partially update time entry approval",
)
def patch_time_entry_approval(
    approval_id: UUID,
    approval_data: TimeEntryApprovalPatch,
    db: Session = Depends(get_db),
):

    approval = get_time_entry_approval_or_404(
        approval_id,
        db,
    )

    update_data = approval_data.model_dump(
        exclude_unset=True
    )

    if "manual_time_entry_id" in update_data:

        manual_entry = db.scalar(
            select(ManualTimeEntry).where(
                ManualTimeEntry.id == update_data["manual_time_entry_id"]
            )
        )

        if manual_entry is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manual time entry not found.",
            )

    # Auto-set approved_at if status is being changed to non-pending
    # and approved_at wasn't explicitly provided in this patch
    if (
        "status" in update_data
        and update_data["status"] != TimeEntryApprovalStatus.pending
        and "approved_at" not in update_data
    ):
        update_data["approved_at"] = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(approval, field, value)

    approval.updated_at = datetime.now(timezone.utc)

    try:

        db.commit()
        db.refresh(approval)

    except IntegrityError as e:

        db.rollback()
        handle_integrity_error(e)

    return approval


@router.delete(
    "/{approval_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete time entry approval",
)
def delete_time_entry_approval(
    approval_id: UUID,
    db: Session = Depends(get_db),
):

    approval = get_time_entry_approval_or_404(
        approval_id,
        db,
    )

    db.delete(approval)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )