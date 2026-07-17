from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import Date, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.time_entries import TimeEntry

from app.schemas.time_entries import (
    TimeEntryCreate,
    TimeEntryPatch,
    TimeEntryResponse,
    TimeEntryStartRequest,
    TimeEntryStopRequest,
    TimeEntryUpdate,
)

router = APIRouter(
    prefix="/time-entries",
    tags=["Time Entries"],
)


def get_time_entry_or_404(
    entry_id: int,
    db: Session,
) -> TimeEntry:
    entry = db.scalar(
        select(TimeEntry).where(
            TimeEntry.id == entry_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found.",
        )

    return entry


@router.get(
    "",
    response_model=list[TimeEntryResponse],
    summary="Get all time entries",
)
def get_time_entries(
    organization: int | None = Query(
        default=None,
        description="Filter by Organization ID",
    ),
    user: int | None = Query(
        default=None,
        description="Filter by User ID",
    ),
    project: int | None = Query(
        default=None,
        description="Filter by Project ID",
    ),
    task: int | None = Query(
        default=None,
        description="Filter by Task ID",
    ),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by Status",
    ),
    is_manual: bool | None = Query(
        default=None,
        description="Filter Manual Entries",
    ),
    is_billable: bool | None = Query(
        default=None,
        description="Filter Billable Entries",
    ),
    start_date: str | None = Query(
        default=None,
        description="Filter by Start Date (YYYY-MM-DD)",
    ),
    db: Session = Depends(get_db),
):
    query = select(TimeEntry)

    if organization is not None:
        query = query.where(
            TimeEntry.organization_id == organization
        )

    if user is not None:
        query = query.where(
            TimeEntry.user_id == user
        )

    if project is not None:
        query = query.where(
            TimeEntry.project_id == project
        )

    if task is not None:
        query = query.where(
            TimeEntry.task_id == task
        )

    if status_filter is not None:
        query = query.where(
            TimeEntry.status == status_filter
        )

    if is_manual is not None:
        query = query.where(
            TimeEntry.is_manual == is_manual
        )

    if is_billable is not None:
        query = query.where(
            TimeEntry.is_billable == is_billable
        )

    if start_date is not None:
        query = query.where(
            TimeEntry.start_time.cast(Date) == start_date
        )

    return db.scalars(query).all()

@router.get(
    "/{entry_id}",
    response_model=TimeEntryResponse,
    summary="Get time entry by ID",
)
def get_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
):
    return get_time_entry_or_404(
        entry_id,
        db,
    )

def validate_time_entry(
    start_time: datetime,
    end_time: datetime | None,
    total_seconds: int,
):
    if (
        end_time is not None
        and end_time < start_time
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time cannot be earlier than start time.",
        )

    if total_seconds < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total seconds cannot be negative.",
        )
    

    
@router.post(
    "",
    response_model=TimeEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create time entry",
)
def create_time_entry(
    entry_data: TimeEntryCreate,
    db: Session = Depends(get_db),
):
    validate_time_entry(
        start_time=entry_data.start_time,
        end_time=entry_data.end_time,
        total_seconds=entry_data.total_seconds,
    )

    new_entry = TimeEntry(
        **entry_data.model_dump()
    )

    try:
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

    except IntegrityError as e:
        db.rollback()

        error = str(e.orig)

        if "time_entries_organization_id_fkey" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        if "time_entries_project_id_fkey" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
    )

    return new_entry


@router.put(
    "/{entry_id}",
    response_model=TimeEntryResponse,
    summary="Update time entry",
)
def update_time_entry(
    entry_id: int,
    entry_data: TimeEntryUpdate,
    db: Session = Depends(get_db),
):
    entry = get_time_entry_or_404(entry_id, db)

    update_data = entry_data.model_dump()
    for field, value in update_data.items():
        setattr(entry, field, value)

    validate_time_entry(
        start_time=entry.start_time,
        end_time=entry.end_time,
        total_seconds=entry.total_seconds,
    )

    entry.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(entry)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return entry


@router.patch(
    "/{entry_id}",
    response_model=TimeEntryResponse,
    summary="Partially update time entry",
)
def patch_time_entry(
    entry_id: int,
    entry_data: TimeEntryPatch,
    db: Session = Depends(get_db),
):
    entry = get_time_entry_or_404(
        entry_id,
        db,
    )

    update_data = entry_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    # validate AFTER applying the patch, using final values
    validate_time_entry(
        start_time=entry.start_time,
        end_time=entry.end_time,
        total_seconds=entry.total_seconds,
    )

    entry.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(entry)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return entry


#start_time API
@router.post(
    "/start",
    response_model=TimeEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start time entry",
)
def start_time_entry(
    request: TimeEntryStartRequest,
    db: Session = Depends(get_db),
):
    running_entry = db.scalar(
        select(TimeEntry).where(
            TimeEntry.user_id == request.user_id,
            TimeEntry.status == "running",
        )
    )

    if running_entry:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A timer is already running.",
        )

    new_entry = TimeEntry(
        organization_id=request.organization_id,
        user_id=request.user_id,
        project_id=request.project_id,
        task_id=request.task_id,
        start_time=datetime.utcnow(),
        end_time=None,
        total_seconds=0,
        status="running",
        is_manual=request.is_manual,
        is_billable=request.is_billable,
        description=request.description,
    )

    try:
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "time_entries_organization_id_fkey" in error:
            raise HTTPException(
                status_code=404,
                detail="Organization not found.",
            )

        if "time_entries_project_id_fkey" in error:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        raise HTTPException(
            status_code=500,
            detail="Database error.",
        )

    return new_entry

#stop_time API

@router.post(
    "/stop",
    response_model=TimeEntryResponse,
    summary="Stop running time entry",
)
def stop_time_entry(
    request: TimeEntryStopRequest,
    db: Session = Depends(get_db),
):
    running_entry = db.scalar(
        select(TimeEntry).where(
            TimeEntry.user_id == request.user_id,
            TimeEntry.status == "running",
        )
    )

    if running_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No running timer found.",
        )

    running_entry.end_time = datetime.utcnow()

    running_entry.total_seconds = int(
        (
            running_entry.end_time
            - running_entry.start_time
        ).total_seconds()
    )

    running_entry.status = "stopped"
    running_entry.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(running_entry)

    return running_entry

@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete time entry",
)
def delete_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
):
    entry = get_time_entry_or_404(
        entry_id,
        db,
    )

    db.delete(entry)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
