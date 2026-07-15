from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PermissionResponse(BaseModel):
    id: UUID
    permission_name: str
    module: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class PermissionCreate(BaseModel):
    permission_name: str = Field(
        min_length=1,
        max_length=150,
    )

    module: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = None


class PermissionUpdate(BaseModel):
    permission_name: str = Field(
        min_length=1,
        max_length=150,
    )

    module: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = None


class PermissionPatch(BaseModel):
    permission_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    module: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = None