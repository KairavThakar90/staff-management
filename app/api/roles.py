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
from app.models.roles import Role
from app.schemas.roles import (
    RoleCreate,
    RolePatch,
    RoleResponse,
    RoleUpdate,
)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


def get_role_or_404(
    role_id: UUID,
    db: Session,
) -> Role:
    role = db.scalar(
        select(Role).where(
            Role.id == role_id
        )
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    return role


@router.get(
    "",
    response_model=list[RoleResponse],
    summary="Get all roles",
    description="Returns all roles.",
)
def get_roles(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Role)
    ).all()


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get role by ID",
    description="Returns a role by UUID.",
)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db),
):
    return get_role_or_404(
        role_id,
        db,
    )


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create role",
    description="Creates a new role.",
)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
):
    new_role = Role(
        **role.model_dump()
    )

    try:
        db.add(new_role)
        db.commit()
        db.refresh(new_role)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "uq_roles_org_name" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists in this organization.",
            )

        if "fk_roles_organization" in error:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return new_role

@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update role",
    description="Replace an existing role.",
)
def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
):
    role = get_role_or_404(
        role_id,
        db,
    )

    update_data = role_data.model_dump()

    for field, value in update_data.items():
        setattr(role, field, value)

    try:
        db.commit()
        db.refresh(role)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "uq_roles_org_name" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists in this organization.",
            )

        if "fk_roles_organization" in error:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return role


@router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Partially update role",
    description="Update one or more fields of a role.",
)
def patch_role(
    role_id: UUID,
    role_data: RolePatch,
    db: Session = Depends(get_db),
):
    role = get_role_or_404(
        role_id,
        db,
    )

    update_data = role_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(role, field, value)

    try:
        db.commit()
        db.refresh(role)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "uq_roles_org_name" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists in this organization.",
            )

        if "fk_roles_organization" in error:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return role


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete role",
    description="Delete a role.",
)
def delete_role(
    role_id: UUID,
    db: Session = Depends(get_db),
):
    role = get_role_or_404(
        role_id,
        db,
    )

    db.delete(role)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )