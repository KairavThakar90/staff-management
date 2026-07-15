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

from app.core.security import hash_password
from app.db.database import get_db
from app.models.users import User
from app.schemas.users import (
    UserCreate,
    UserPatch,
    UserResponse,
    UserUpdate,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def get_user_or_404(
    user_id: UUID,
    db: Session,
) -> User:
    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Get all users",
    description="Returns all users.",
)
def get_users(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(User)
    ).all()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Returns a user by UUID.",
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return get_user_or_404(
        user_id,
        db,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Creates a new user.",
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    user_data = user.model_dump()

    password = user_data.pop("password")

    user_data["password_hash"] = hash_password(
        password
    )

    new_user = User(
        **user_data,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "uq_users_org_email" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists in this organization.",
            )

        if "fk_users_organization" in error:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return new_user
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Replace an existing user.",
)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = get_user_or_404(
        user_id,
        db,
    )

    update_data = user_data.model_dump()

    password = update_data.pop("password")
    update_data["password_hash"] = hash_password(password)

    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "uq_users_org_email" in error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists in this organization.",
            )

        if "fk_users_organization" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Partially update user",
    description="Update one or more fields of a user.",
)
def patch_user(
    user_id: UUID,
    user_data: UserPatch,
    db: Session = Depends(get_db),
):
    user = get_user_or_404(
        user_id,
        db,
    )

    update_data = user_data.model_dump(
        exclude_unset=True
    )

    if "password" in update_data:
        password = update_data.pop("password")
        update_data["password_hash"] = hash_password(password)

    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError as e:

        db.rollback()

        error = str(e.orig)

        if "uq_users_org_email" in error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists in this organization.",
            )

        if "fk_users_organization" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user.",
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    user = get_user_or_404(
        user_id,
        db,
    )

    db.delete(user)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )