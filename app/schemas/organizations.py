from datetime import datetime

from app.enums.organization_status import OrganizationStatus
from pydantic import BaseModel, ConfigDict, Field


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    logo_url: str | None
    timezone: str
    currency: str
    status: OrganizationStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    slug: str = Field(min_length=1, max_length=150)
    logo_url: str | None = None
    timezone: str = Field(min_length=1, max_length=100)
    currency: str = Field(min_length=3, max_length=3)
    status: OrganizationStatus = OrganizationStatus.active  # add this

class OrganizationUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    slug: str = Field(min_length=1, max_length=150)
    logo_url: str | None = None
    timezone: str = Field(min_length=1, max_length=100)
    currency: str = Field(min_length=3, max_length=3)

class OrganizationPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    slug: str | None = Field(default=None, min_length=1, max_length=150)
    logo_url: str | None = None
    timezone: str | None = Field(default=None, min_length=1, max_length=100)
    currency: str | None = Field(default=None, min_length=3, max_length=3)