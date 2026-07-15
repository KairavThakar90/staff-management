from datetime import datetime
from typing import Optional
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
from app.models.projects import Project
from app.models.tasks import Task
from app.schemas.tasks import (
    TaskCreate,
    TaskPatch,
    TaskResponse,
    TaskUpdate,
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


def get_task_or_404(
    task_id: UUID,
    db: Session,
) -> Task:
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.deleted_at.is_(None),
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return task


@router.get(
    "",
    response_model=list[TaskResponse],
    summary="Get all tasks (optionally filter by project)",
)
def get_tasks(
    project: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    query = select(Task).where(Task.deleted_at.is_(None))

    if project is not None:
        proj = db.scalar(
            select(Project).where(
                Project.id == project,
                Project.deleted_at.is_(None),
            )
        )

        if proj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        query = query.where(Task.project_id == project)

    return db.scalars(query).all()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID",
)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    return get_task_or_404(
        task_id,
        db,
    )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
):
    project = db.scalar(
        select(Project).where(
            Project.id == task.project_id,
            Project.deleted_at.is_(None),
        )
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    new_task = Task(
        **task.model_dump()
    )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return new_task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = get_task_or_404(
        task_id,
        db,
    )

    project = db.scalar(
        select(Project).where(
            Project.id == task_data.project_id,
            Project.deleted_at.is_(None),
        )
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    update_data = task_data.model_dump()

    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(task)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return task


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partially update task",
)
def patch_task(
    task_id: UUID,
    task_data: TaskPatch,
    db: Session = Depends(get_db),
):
    task = get_task_or_404(
        task_id,
        db,
    )

    update_data = task_data.model_dump(
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

    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(task)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete task",
)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    task = get_task_or_404(
        task_id,
        db,
    )

    task.deleted_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()

    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )