from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.organizations import Organization
from app.schemas.organizations import (
    OrganizationCreate,
    OrganizationPatch,
    OrganizationResponse,
    OrganizationUpdate,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get(
    "",
    response_model=list[OrganizationResponse],
    summary="Get all organizations",
    description="Returns a list of all organizations.",
)
def get_organizations(
    db: Session = Depends(get_db),
):
    organizations = db.scalars(
        select(Organization)
    ).all()

    return organizations


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Get organization by ID",
    description="Returns a single organization by its ID.",
)
def get_organization_by_id(
    organization_id: int,
    db: Session = Depends(get_db),
):
    organization = db.scalar(
        select(Organization).where(
            Organization.id == organization_id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return organization


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
    description="Creates a new organization.",
)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
):
    new_organization = Organization(
        name=organization.name,
        slug=organization.slug,
        logo_url=organization.logo_url,
        timezone=organization.timezone,
        currency=organization.currency,
        status=organization.status,
    )

    try:
        db.add(new_organization)
        db.commit()
        db.refresh(new_organization)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization slug already exists.",
        )

    return new_organization


@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Update organization",
    description="Updates an existing organization.",
)
def update_organization(
    organization_id: int,
    organization_data: OrganizationUpdate,
    db: Session = Depends(get_db),
):
    organization = db.scalar(
        select(Organization).where(
            Organization.id == organization_id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    organization.name = organization_data.name
    organization.slug = organization_data.slug
    organization.logo_url = organization_data.logo_url
    organization.timezone = organization_data.timezone
    organization.currency = organization_data.currency
    organization.status = organization_data.status

    try:
        db.commit()
        db.refresh(organization)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization slug already exists.",
        )

    return organization


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete organization",
    description="Deletes an organization by its ID.",
)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
):
    organization = db.scalar(
        select(Organization).where(
            Organization.id == organization_id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    db.delete(organization)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )

#patch
@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Partially update organization",
    description="Updates only the provided organization fields.",
)
def patch_organization(
    organization_id: int,
    organization_data: OrganizationPatch,
    db: Session = Depends(get_db),
):
    organization = db.scalar(
        select(Organization).where(
            Organization.id == organization_id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    update_data = organization_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(organization, field, value)

    try:
        db.commit()
        db.refresh(organization)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization slug already exists.",
        )

    return organization










             