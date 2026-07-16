from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.api_error_logs import APIErrorLog
from app.schemas.api_error_logs import (
    APIErrorLogCreate,
    APIErrorLogPatch,
    APIErrorLogResponse,
    APIErrorLogUpdate,
)

router = APIRouter(
    prefix="/api-error-logs",
    tags=["API Error Logs"],
)


def get_api_error_log_or_404(
    log_id: int,
    db: Session,
) -> APIErrorLog:
    log_item = db.scalar(
        select(APIErrorLog).where(
            APIErrorLog.id == log_id
        )
    )

    if log_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API error log not found.",
        )

    return log_item


@router.get(
    "",
    response_model=list[APIErrorLogResponse],
    summary="Get all API error logs",
)
def get_api_error_logs(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(APIErrorLog)
    ).all()


@router.get(
    "/{log_id}",
    response_model=APIErrorLogResponse,
    summary="Get API error log by ID",
)
def get_api_error_log(
    log_id: int,
    db: Session = Depends(get_db),
):
    return get_api_error_log_or_404(
        log_id,
        db,
    )


@router.post(
    "",
    response_model=APIErrorLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API error log",
)
def create_api_error_log(
    log_data: APIErrorLogCreate,
    db: Session = Depends(get_db),
):
    new_log = APIErrorLog(
        **log_data.model_dump()
    )

    try:
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating API error log.",
        )

    return new_log


@router.put(
    "/{log_id}",
    response_model=APIErrorLogResponse,
    summary="Update API error log",
)
def update_api_error_log(
    log_id: int,
    log_data: APIErrorLogUpdate,
    db: Session = Depends(get_db),
):
    log_item = get_api_error_log_or_404(
        log_id,
        db,
    )

    update_data = log_data.model_dump()

    for field, value in update_data.items():
        setattr(log_item, field, value)

    try:
        db.commit()
        db.refresh(log_item)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating API error log.",
        )

    return log_item


@router.patch(
    "/{log_id}",
    response_model=APIErrorLogResponse,
    summary="Partially update API error log",
)
def patch_api_error_log(
    log_id: int,
    log_data: APIErrorLogPatch,
    db: Session = Depends(get_db),
):
    log_item = get_api_error_log_or_404(
        log_id,
        db,
    )

    update_data = log_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(log_item, field, value)

    try:
        db.commit()
        db.refresh(log_item)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while patching API error log.",
        )

    return log_item
