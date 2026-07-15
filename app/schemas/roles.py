from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleResponse(BaseModel):
    id: UUID
    organization_id: UUID
    role_name: str
    description: str | None
    is_system_role: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class RoleCreate(BaseModel):
    organization_id: UUID

    role_name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    is_system_role: bool = False


class RoleUpdate(BaseModel):
    organization_id: UUID

    role_name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    is_system_role: bool


class RolePatch(BaseModel):
    organization_id: UUID | None = None

    role_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    is_system_role: bool | None = None