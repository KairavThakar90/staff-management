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
    TimeEntryAppUsageOrganizationSummaryResponse,
    TimeEntryAppUsagePatch,
    TimeEntryAppUsageResponse,
    TimeEntryAppUsageSummaryResponse,
    TimeEntryAppUsageDateRangeSummaryResponse,
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
    "/summary/by-application",
    response_model=list[TimeEntryAppUsageSummaryResponse],
    summary="Get application-wise usage summary",
)
def get_application_wise_usage_summary(
    organization: int | None = None,
    time_entry: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    query = select(
        TimeEntryAppUsage.application_name,
        func.sum(
            TimeEntryAppUsage.duration_seconds
        ).label("total_duration_seconds"),
    )

    if organization is not None:
        query = query.where(
            TimeEntryAppUsage.organization_id == organization
        )

    if time_entry is not None:
        query = query.where(
            TimeEntryAppUsage.time_entry_id == time_entry
        )

    if from_date is not None:
        query = query.where(
            TimeEntryAppUsage.recorded_at >= from_date
        )

    if to_date is not None:
        query = query.where(
            TimeEntryAppUsage.recorded_at < (
                to_date + timedelta(days=1)
            )
        )

    query = query.group_by(
        TimeEntryAppUsage.application_name
    ).order_by(
        func.sum(
            TimeEntryAppUsage.duration_seconds
        ).desc()
    )

    results = db.execute(query).all()

    return [
        TimeEntryAppUsageSummaryResponse(
            application_name=row.application_name,
            total_duration_seconds=row.total_duration_seconds or 0,
        )
        for row in results
    ]



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
    "/summary/by-organization",
    response_model=list[TimeEntryAppUsageOrganizationSummaryResponse],
    summary="Get organization-wise usage summary",
)
def get_organization_wise_usage_summary(
    organization: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    query = select(
        TimeEntryAppUsage.organization_id,
        func.sum(
            TimeEntryAppUsage.duration_seconds
        ).label("total_duration_seconds"),
    )

    if organization is not None:
        query = query.where(
            TimeEntryAppUsage.organization_id == organization
        )

    if from_date is not None:
        query = query.where(
            TimeEntryAppUsage.recorded_at >= from_date
        )

    if to_date is not None:
        query = query.where(
            TimeEntryAppUsage.recorded_at < (
                to_date + timedelta(days=1)
            )
        )

    query = query.group_by(
        TimeEntryAppUsage.organization_id
    ).order_by(
        func.sum(
            TimeEntryAppUsage.duration_seconds
        ).desc()
    )

    results = db.execute(query).all()

    return [
        TimeEntryAppUsageOrganizationSummaryResponse(
            organization_id=row.organization_id,
            total_duration_seconds=row.total_duration_seconds or 0,
        )
        for row in results
    ]


@router.get(
    "/summary/{time_entry_id}",
    response_model=list[TimeEntryAppUsageSummaryResponse],
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



@router.get(
    "/date-range-summary",
    response_model=TimeEntryAppUsageDateRangeSummaryResponse,
    summary="Get app usage summary by date range",
)
def get_app_usage_date_range_summary(
    from_date: date,
    to_date: date,
    db: Session = Depends(get_db),
):
    if from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_date cannot be greater than to_date.",
        )

    # Make the `to_date` filter inclusive.
    # Example:
    # from_date = 2026-07-21
    # to_date   = 2026-07-21
    #
    # This includes all records from:
    # 2026-07-21 00:00:00
    # through
    # 2026-07-21 23:59:59...
    end_date = to_date + timedelta(days=1)

    # Total application usage duration
    total_usage_seconds = db.scalar(
        select(
            func.coalesce(
                func.sum(TimeEntryAppUsage.duration_seconds),
                0,
            )
        ).where(
            TimeEntryAppUsage.recorded_at >= from_date,
            TimeEntryAppUsage.recorded_at < end_date,
        )
    )

    # Number of distinct applications used
    application_count = db.scalar(
        select(
            func.count(
                func.distinct(
                    TimeEntryAppUsage.application_name
                )
            )
        ).where(
            TimeEntryAppUsage.recorded_at >= from_date,
            TimeEntryAppUsage.recorded_at < end_date,
        )
    )

    # Get all related time_entry IDs for the selected date range
    time_entry_ids = db.scalars(
        select(
            TimeEntryAppUsage.time_entry_id
        ).where(
            TimeEntryAppUsage.recorded_at >= from_date,
            TimeEntryAppUsage.recorded_at < end_date,
        ).distinct()
    ).all()

    # Fetch total_seconds from time_entries
    # for the time entries used in this date range.
    total_duration_seconds = 0

    if time_entry_ids:
        total_duration_seconds = db.scalar(
            select(
                func.coalesce(
                    func.sum(TimeEntry.total_seconds),
                    0,
                )
            ).where(
                TimeEntry.id.in_(time_entry_ids)
            )
        )

    return {
        "from_date": from_date,
        "to_date": to_date,
        "total_usage_seconds": total_usage_seconds,
        "total_duration_seconds": total_duration_seconds,
        "application_count": application_count,
    }


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
