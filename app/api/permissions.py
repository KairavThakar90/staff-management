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
from app.models.permissions import Permission
from app.schemas.permissions import (
    PermissionCreate,
    PermissionPatch,
    PermissionResponse,
    PermissionUpdate,
)

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


def get_permission_or_404(
    permission_id: UUID,
    db: Session,
) -> Permission:
    permission = db.scalar(
        select(Permission).where(
            Permission.id == permission_id
        )
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found.",
        )

    return permission


@router.get(
    "",
    response_model=list[PermissionResponse],
    summary="Get all permissions",
    description="Returns all permissions.",
)
def get_permissions(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Permission)
    ).all()


@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Get permission by ID",
    description="Returns a permission by UUID.",
)
def get_permission(
    permission_id: UUID,
    db: Session = Depends(get_db),
):
    return get_permission_or_404(
        permission_id,
        db,
    )


@router.post(
    "",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create permission",
    description="Creates a new permission.",
)
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
):
    new_permission = Permission(
        **permission.model_dump()
    )

    try:
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "uq_permissions_name" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already exists.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return new_permission


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Update permission",
    description="Replace an existing permission.",
)
def update_permission(
    permission_id: UUID,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
):
    permission = get_permission_or_404(
        permission_id,
        db,
    )

    update_data = permission_data.model_dump()

    for field, value in update_data.items():
        setattr(permission, field, value)

    try:
        db.commit()
        db.refresh(permission)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "uq_permissions_name" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already exists.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return permission


@router.patch(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Partially update permission",
    description="Update one or more fields of a permission.",
)
def patch_permission(
    permission_id: UUID,
    permission_data: PermissionPatch,
    db: Session = Depends(get_db),
):
    permission = get_permission_or_404(
        permission_id,
        db,
    )

    update_data = permission_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(permission, field, value)

    try:
        db.commit()
        db.refresh(permission)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "uq_permissions_name" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already exists.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return permission


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete permission",
    description="Delete a permission.",
)
def delete_permission(
    permission_id: UUID,
    db: Session = Depends(get_db),
):
    permission = get_permission_or_404(
        permission_id,
        db,
    )

    db.delete(permission)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )