from datetime import date, datetime, timedelta , UTC

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select,func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.time_entry_app_usage import TimeEntryAppUsage
from app.models.time_entries import TimeEntry

from app.schemas.time_entry_app_usage import (
    TimeEntryAppUsageCreate,
    TimeEntryAppUsagePatch,
    TimeEntryAppUsageResponse,
    TimeEntryAppUsageUpdate,
)

router = APIRouter(
    prefix="/time-entry-app-usage",
    tags=["Time Entry App Usage"],
)


def get_time_entry_app_usage_or_404(
    usage_id: int,
    db: Session,
) -> TimeEntryAppUsage:
    usage = db.scalar(
        select(TimeEntryAppUsage).where(
            TimeEntryAppUsage.id == usage_id,
        )
    )

    if usage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry app usage not found.",
        )

    return usage


@router.get(
    "",
    response_model=list[TimeEntryAppUsageResponse],
    summary="Get all app usage records with optional filters",
)
def get_time_entry_app_usage(
    organization: int | None = None,
    time_entry: int | None = None,
    app: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    query = select(TimeEntryAppUsage)

    # Filter by organization ID
    if organization is not None:
        query = query.where(
            TimeEntryAppUsage.organization_id == organization
        )

    # Filter by time entry ID
    if time_entry is not None:
        query = query.where(
            TimeEntryAppUsage.time_entry_id == time_entry
        )

    # Filter by application name
    if app is not None:
        query = query.where(
            TimeEntryAppUsage.application_name == app
        )

    # Filter records from the given date
    if from_date is not None:
        from_datetime = datetime.combine(
            from_date,
            datetime.min.time(),
        )

        query = query.where(
            TimeEntryAppUsage.recorded_at >= from_datetime
        )

    # Filter records up to and including the given date
    if to_date is not None:
        to_datetime = datetime.combine(
            to_date + timedelta(days=1),
            datetime.min.time(),
        )

        query = query.where(
            TimeEntryAppUsage.recorded_at < to_datetime
        )

    # Return newest records first
    query = query.order_by(
        TimeEntryAppUsage.recorded_at.desc()
    )

    return db.scalars(query).all()

@router.get(
    "/{usage_id}",
    response_model=TimeEntryAppUsageResponse,
    summary="Get app usage by ID",
)
def get_app_usage_by_id(
    usage_id: int,
    db: Session = Depends(get_db),
):
    return get_time_entry_app_usage_or_404(usage_id, db)

@router.get(
    "/summary/{time_entry_id}",
    summary="Get application usage summary for a time entry",
)
def get_application_usage_summary(
    time_entry_id: int,
    db: Session = Depends(get_db),
):
    results = db.execute(
        select(
            TimeEntryAppUsage.application_name,
            func.sum(
                TimeEntryAppUsage.duration_seconds
            ).label("total_duration_seconds"),
        )
        .where(
            TimeEntryAppUsage.time_entry_id == time_entry_id
        )
        .group_by(
            TimeEntryAppUsage.application_name
        )
        .order_by(
            func.sum(
                TimeEntryAppUsage.duration_seconds
            ).desc()
        )
    ).all()

    return [
        {
            "application_name": row.application_name,
            "total_duration_seconds": row.total_duration_seconds,
        }
        for row in results
    ]

@router.post(
    "",
    response_model=TimeEntryAppUsageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create app usage record",
)
def create_time_entry_app_usage(
    usage_data: TimeEntryAppUsageCreate,
    db: Session = Depends(get_db),
):
    time_entry = db.scalar(
        select(TimeEntry).where(
            TimeEntry.id == usage_data.time_entry_id
        )
    )

    if time_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found.",
        )

    if time_entry.status != "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot record app usage for a stopped time entry.",
        )

    if time_entry.organization_id != usage_data.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization does not match the selected time entry.",
        )

    new_usage = TimeEntryAppUsage(
        **usage_data.model_dump(exclude_none=True)
    )

    try:
        db.add(new_usage)
        db.commit()
        db.refresh(new_usage)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "fk_time_entry_app_usage_entry" in error or "time_entry_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time entry not found.",
            )

        if "fk_time_entry_app_usage_org" in error or "organization_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return new_usage


@router.put(
    "/{usage_id}",
    response_model=TimeEntryAppUsageResponse,
    summary="Update app usage record",
)
def update_time_entry_app_usage(
    usage_id: int,
    usage_data: TimeEntryAppUsageUpdate,
    db: Session = Depends(get_db),
):
    usage = get_time_entry_app_usage_or_404(usage_id, db)

    update_data = usage_data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(usage, field, value)

    usage.updated_at = datetime.now(UTC)

    try:
        db.commit()
        db.refresh(usage)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "fk_time_entry_app_usage_entry" in error or "time_entry_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time entry not found.",
            )

        if "fk_time_entry_app_usage_org" in error or "organization_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return usage


@router.patch(
    "/{usage_id}",
    response_model=TimeEntryAppUsageResponse,
    summary="Partially update app usage record",
)
def patch_time_entry_app_usage(
    usage_id: int,
    usage_data: TimeEntryAppUsagePatch,
    db: Session = Depends(get_db),
):
    usage = get_time_entry_app_usage_or_404(usage_id, db)

    update_data = usage_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(usage, field, value)

    usage.updated_at = datetime.now(UTC)

    try:
        db.commit()
        db.refresh(usage)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "fk_time_entry_app_usage_entry" in error or "time_entry_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time entry not found.",
            )

        if "fk_time_entry_app_usage_org" in error or "organization_id" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return usage


@router.delete(
    "/{usage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete app usage record",
)
def delete_time_entry_app_usage(
    usage_id: int,
    db: Session = Depends(get_db),
):
    usage = get_time_entry_app_usage_or_404(usage_id, db)

    db.delete(usage)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
