from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Response, Query, status
from app.db.database import get_db
from app.models.projects import Project
from app.schemas.projects import (
    ProjectCreate,
    ProjectPatch,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


def get_project_or_404(
    project_id: int,
    db: Session,
) -> Project:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
        )
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return project


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="Get all projects",
)
def get_projects(
    organization: int | None = Query(
        default=None,
        description="Filter projects by organization ID",
    ),
    db: Session = Depends(get_db),
):
    query = select(Project)

    if organization is not None:
        query = query.where(
            Project.organization_id == organization
        )

    return db.scalars(query).all()

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    return get_project_or_404(
        project_id,
        db,
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    new_project = Project(
        **project.model_dump()
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

    except IntegrityError as e:
        db.rollback()
        error = str(e.orig)

        if "fk_projects_organization" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return new_project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(
        project_id,
        db,
    )

    update_data = project_data.model_dump()
    for field, value in update_data.items():
        setattr(project, field, value)
    project.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(project)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Partially update project",
)
def patch_project(
    project_id: int,
    project_data: ProjectPatch,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(
        project_id,
        db,
    )

    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    project.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(project)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(
        project_id,
        db,
    )

    db.delete(project)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
