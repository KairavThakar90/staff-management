from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.time_entries import TimeEntry
from app.schemas.time_entries import (
    TimeEntryCreate,
    TimeEntryPatch,
    TimeEntryResponse,
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
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(TimeEntry)
    ).all()


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
    entry = get_time_entry_or_404(
        entry_id,
        db,
    )

    update_data = entry_data.model_dump()
    for field, value in update_data.items():
        setattr(entry, field, value)
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
