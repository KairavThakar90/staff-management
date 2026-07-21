from datetime import date, datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
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
    organization: int | None = Query(
        default=None,
        description="Filter activity records by organization ID",
    ),
    time_entry: int | None = Query(
        default=None,
        description="Filter activity records by time entry ID",
    ),
    recorded_date: date | None = Query(
        default=None,
        description="Filter activity records by recorded date",
    ),
    db: Session = Depends(get_db),
):
    query = select(TimeEntryActivity)

    if organization is not None:
        query = query.where(
            TimeEntryActivity.organization_id == organization
        )

    if time_entry is not None:
        query = query.where(
            TimeEntryActivity.time_entry_id == time_entry
        )

    if recorded_date is not None:
        query = query.where(
            TimeEntryActivity.recorded_at.cast(date) == recorded_date
        )

    query = query.order_by(
        TimeEntryActivity.recorded_at.desc()
    )

    return db.scalars(query).all()


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
    try:
        # 1. Verify organization
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

        # 2. Verify time entry
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

        # 3. Verify organization
        if time_entry.organization_id != activity_data.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization does not match the selected time entry.",
            )

        # 4. Verify running status
        if time_entry.status != "running":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot record activity for a stopped time entry.",
            )

        # 5. Create activity
        new_activity = TimeEntryActivity(
            **activity_data.model_dump(exclude_none=True)
        )

        db.add(new_activity)
        db.commit()
        db.refresh(new_activity)

        return new_activity

    except HTTPException:
        raise

    except IntegrityError as e:
            db.rollback()

            print("TIME ENTRY ACTIVITY DB ERROR:", str(e.orig))

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while creating time entry activity.",
            )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {type(e).__name__}: {str(e)}",
        )



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
