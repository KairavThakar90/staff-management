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
from uuid import UUID

from app.db.database import get_db
from app.models.projects import Project
from app.models.tasks import Task
from app.models.time_sessions import TimeSession
from app.schemas.time_sessions import (
    TimeSessionCreate,
    TimeSessionPatch,
    TimeSessionResponse,
    TimeSessionUpdate,
)

router = APIRouter(
    prefix="/time-sessions",
    tags=["Time Sessions"],
)


def get_time_session_or_404(
    session_id: UUID,
    db: Session,
) -> TimeSession:

    session = db.scalar(
        select(TimeSession).where(
            TimeSession.id == session_id
        )
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time session not found.",
        )

    return session


@router.get(
    "",
    response_model=list[TimeSessionResponse],
    summary="Get all time sessions",
)
def get_time_sessions(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(TimeSession)
    ).all()


@router.get(
    "/{session_id}",
    response_model=TimeSessionResponse,
    summary="Get time session by ID",
)
def get_time_session(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    return get_time_session_or_404(
        session_id,
        db,
    )


@router.post(
    "",
    response_model=TimeSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create time session",
)
def create_time_session(
    session_data: TimeSessionCreate,
    db: Session = Depends(get_db),
):

    project = db.scalar(
        select(Project).where(
            Project.id == session_data.project_id,
            Project.deleted_at.is_(None),
        )
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if session_data.task_id is not None:

        task = db.scalar(
            select(Task).where(
                Task.id == session_data.task_id,
                Task.deleted_at.is_(None),
            )
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

    new_session = TimeSession(
        **session_data.model_dump()
    )

    try:

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "fk_time_sessions_project" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        if "fk_time_sessions_task" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return new_session


@router.put(
    "/{session_id}",
    response_model=TimeSessionResponse,
    summary="Update time session",
)
def update_time_session(
    session_id: UUID,
    session_data: TimeSessionUpdate,
    db: Session = Depends(get_db),
):

    session = get_time_session_or_404(
        session_id,
        db,
    )

    project = db.scalar(
        select(Project).where(
            Project.id == session_data.project_id,
            Project.deleted_at.is_(None),
        )
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if session_data.task_id is not None:

        task = db.scalar(
            select(Task).where(
                Task.id == session_data.task_id,
                Task.deleted_at.is_(None),
            )
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

    update_data = session_data.model_dump()

    for field, value in update_data.items():
        setattr(session, field, value)

    try:

        db.commit()
        db.refresh(session)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "fk_time_sessions_project" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        if "fk_time_sessions_task" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return session


@router.patch(
    "/{session_id}",
    response_model=TimeSessionResponse,
    summary="Partially update time session",
)
def patch_time_session(
    session_id: UUID,
    session_data: TimeSessionPatch,
    db: Session = Depends(get_db),
):

    session = get_time_session_or_404(
        session_id,
        db,
    )

    update_data = session_data.model_dump(
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
        setattr(session, field, value)

    try:

        db.commit()
        db.refresh(session)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "fk_time_sessions_project" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        if "fk_time_sessions_task" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return session


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete time session",
)
def delete_time_session(
    session_id: UUID,
    db: Session = Depends(get_db),
):

    session = get_time_session_or_404(
        session_id,
        db,
    )

    db.delete(session)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )