from datetime import datetime
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
from app.models.manual_time_entries import ManualTimeEntry
from app.models.projects import Project
from app.models.tasks import Task
from app.schemas.manual_time_entries import (
    ManualTimeEntryCreate,
    ManualTimeEntryPatch,
    ManualTimeEntryResponse,
    ManualTimeEntryUpdate,
)

router = APIRouter(
    prefix="/manual-time-entries",
    tags=["Manual Time Entries"],
)


def get_manual_time_entry_or_404(
    entry_id: UUID,
    db: Session,
) -> ManualTimeEntry:

    entry = db.scalar(
        select(ManualTimeEntry).where(
            ManualTimeEntry.id == entry_id
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manual time entry not found.",
        )

    return entry


@router.get(
    "",
    response_model=list[ManualTimeEntryResponse],
    summary="Get all manual time entries",
)
def get_manual_time_entries(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(ManualTimeEntry)
    ).all()


@router.get(
    "/{entry_id}",
    response_model=ManualTimeEntryResponse,
    summary="Get manual time entry by ID",
)
def get_manual_time_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
):
    return get_manual_time_entry_or_404(
        entry_id,
        db,
    )


@router.post(
    "",
    response_model=ManualTimeEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create manual time entry",
)
def create_manual_time_entry(
    entry_data: ManualTimeEntryCreate,
    db: Session = Depends(get_db),
):

    project = db.scalar(
        select(Project).where(
            Project.id == entry_data.project_id,
            Project.deleted_at.is_(None),
        )
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if entry_data.task_id is not None:

        task = db.scalar(
            select(Task).where(
                Task.id == entry_data.task_id,
                Task.deleted_at.is_(None),
            )
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

    new_entry = ManualTimeEntry(
        **entry_data.model_dump()
    )

    try:

        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "fk_manual_time_entries_project" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        if "fk_manual_time_entries_task" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return new_entry


@router.put(
    "/{entry_id}",
    response_model=ManualTimeEntryResponse,
    summary="Update manual time entry",
)
def update_manual_time_entry(
    entry_id: UUID,
    entry_data: ManualTimeEntryUpdate,
    db: Session = Depends(get_db),
):

    entry = get_manual_time_entry_or_404(
        entry_id,
        db,
    )

    project = db.scalar(
        select(Project).where(
            Project.id == entry_data.project_id,
            Project.deleted_at.is_(None),
        )
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if entry_data.task_id is not None:

        task = db.scalar(
            select(Task).where(
                Task.id == entry_data.task_id,
                Task.deleted_at.is_(None),
            )
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

    update_data = entry_data.model_dump()

    for field, value in update_data.items():
        setattr(entry, field, value)

    entry.updated_at = datetime.utcnow()

    try:

        db.commit()
        db.refresh(entry)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "fk_manual_time_entries_project" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        if "fk_manual_time_entries_task" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return entry


@router.patch(
    "/{entry_id}",
    response_model=ManualTimeEntryResponse,
    summary="Partially update manual time entry",
)
def patch_manual_time_entry(
    entry_id: UUID,
    entry_data: ManualTimeEntryPatch,
    db: Session = Depends(get_db),
):

    entry = get_manual_time_entry_or_404(
        entry_id,
        db,
    )

    update_data = entry_data.model_dump(
        exclude_unset=True
    )

    if "project_id" in update_data:

        project = db.scalar(
            select(Project).where(
                Project.id == update_data["project_id"],
                Project.deleted_at.is_(None),
            )
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

    if (
        "task_id" in update_data
        and update_data["task_id"] is not None
    ):

        task = db.scalar(
            select(Task).where(
                Task.id == update_data["task_id"],
                Task.deleted_at.is_(None),
            )
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

    for field, value in update_data.items():
        setattr(entry, field, value)

    entry.updated_at = datetime.utcnow()

    try:

        db.commit()
        db.refresh(entry)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "fk_manual_time_entries_project" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        if "fk_manual_time_entries_task" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return entry


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete manual time entry",
)
def delete_manual_time_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
):

    entry = get_manual_time_entry_or_404(
        entry_id,
        db,
    )

    db.delete(entry)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )