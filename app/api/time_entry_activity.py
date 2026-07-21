from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.time_entry_activity import TimeEntryActivity
from app.models.time_entries import TimeEntry
from app.schemas.time_entry_activity import (
    TimeEntryActivityCreate,
    TimeEntryActivityPatch,
    TimeEntryActivityResponse,
    TimeEntryActivityUpdate,
)

from app.models.organizations import Organization

router = APIRouter(
    prefix="/time-entry-activity",
    tags=["Time Entry Activity"],
)


def get_time_entry_activity_or_404(
    activity_id: int,
    db: Session,
) -> TimeEntryActivity:
    activity = db.scalar(
        select(TimeEntryActivity).where(
            TimeEntryActivity.id == activity_id,
        )
    )

    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry activity not found.",
        )

    return activity


@router.get(
    "",
    response_model=list[TimeEntryActivityResponse],
    summary="Get all time entry activity records",
)
def get_time_entry_activities(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(TimeEntryActivity)
    ).all()


@router.get(
    "/{activity_id}",
    response_model=TimeEntryActivityResponse,
    summary="Get time entry activity by ID",
)
def get_time_entry_activity(
    activity_id: int,
    db: Session = Depends(get_db),
):
    return get_time_entry_activity_or_404(activity_id, db)


@router.post(
    "",
    response_model=TimeEntryActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create time entry activity record",
)
def create_time_entry_activity(
    activity_data: TimeEntryActivityCreate,
    db: Session = Depends(get_db),
):
    # 1. Verify organization exists
    organization_exists = db.scalar(
        select(Organization.id).where(
            Organization.id == activity_data.organization_id
        )
    )

    if organization_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    # 2. Verify time entry exists
    time_entry = db.scalar(
        select(TimeEntry).where(
            TimeEntry.id == activity_data.time_entry_id
        )
    )

    if time_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found.",
        )

    # 3. Verify organization matches
    if time_entry.organization_id != activity_data.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization does not match the selected time entry.",
        )

    # 4. Verify time entry is running
    if time_entry.status != "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot record activity for a stopped time entry.",
        )

    # 5. Create activity
    new_activity = TimeEntryActivity(
        **activity_data.model_dump(exclude_none=True)
    )

    try:
        db.add(new_activity)
        db.commit()
        db.refresh(new_activity)

    except IntegrityError as e:
            db.rollback()

            error = str(e.orig)

            print("TIME ENTRY ACTIVITY DB ERROR:", error)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {error}",
    )
    return new_activity



@router.put(
    "/{activity_id}",
    response_model=TimeEntryActivityResponse,
    summary="Update time entry activity record",
)
def update_time_entry_activity(
    activity_id: int,
    activity_data: TimeEntryActivityUpdate,
    db: Session = Depends(get_db),
):
    activity = get_time_entry_activity_or_404(activity_id, db)

    update_data = activity_data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(activity, field, value)

    activity.updated_at = datetime.now(UTC)

    try:
        db.commit()
        db.refresh(activity)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "fk_time_entry_activity_entry" in error or "time_entry_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time entry not found.",
            )

        if "fk_time_entry_activity_org" in error or "organization_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return activity


@router.patch(
    "/{activity_id}",
    response_model=TimeEntryActivityResponse,
    summary="Partially update time entry activity record",
)
def patch_time_entry_activity(
    activity_id: int,
    activity_data: TimeEntryActivityPatch,
    db: Session = Depends(get_db),
):
    activity = get_time_entry_activity_or_404(activity_id, db)

    update_data = activity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)

    activity.updated_at = datetime.now(UTC)

    try:
        db.commit()
        db.refresh(activity)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "fk_time_entry_activity_entry" in error or "time_entry_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time entry not found.",
            )

        if "fk_time_entry_activity_org" in error or "organization_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return activity


@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete time entry activity record",
)
def delete_time_entry_activity(
    activity_id: int,
    db: Session = Depends(get_db),
):
    activity = get_time_entry_activity_or_404(activity_id, db)

    db.delete(activity)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
