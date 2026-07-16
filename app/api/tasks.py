from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from app.db.database import get_db
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
    task_id: int,
    db: Session,
) -> Task:
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
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
    summary="Get all tasks",
)
def get_tasks(
    organization: int | None = Query(
        default=None,
        description="Filter by organization ID",
    ),
    project: int | None = Query(
        default=None,
        description="Filter by project ID",
    ),
    db: Session = Depends(get_db),
):
    query = select(Task)

    if organization is not None:
        query = query.where(
            Task.organization_id == organization
        )

    if project is not None:
        query = query.where(
            Task.project_id == project
        )

    return db.scalars(query).all()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID",
)
def get_task(
    task_id: int,
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
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    new_task = Task(
        **task_data.model_dump()
    )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "fk_tasks_organization" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        if "fk_tasks_project" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

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
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = get_task_or_404(
        task_id,
        db,
    )

    update_data = task_data.model_dump()
    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(task)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "fk_tasks_organization" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        if "fk_tasks_project" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

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
    task_id: int,
    task_data: TaskPatch,
    db: Session = Depends(get_db),
):
    task = get_task_or_404(
        task_id,
        db,
    )

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(task)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "fk_tasks_organization" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        if "fk_tasks_project" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = get_task_or_404(
        task_id,
        db,
    )

    db.delete(task)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
