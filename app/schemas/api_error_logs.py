from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class APIErrorLogResponse(BaseModel):
    id: int
    organization_id: int | None
    user_id: int | None
    request_id: UUID
    endpoint: str
    http_method: str
    request_headers: dict[str, Any] | None
    request_body: dict[str, Any] | None
    response_status: int
    error_code: str | None
    error_message: str
    stack_trace: str | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIErrorLogCreate(BaseModel):
    organization_id: int | None = None
    user_id: int | None = None
    endpoint: str = Field(min_length=1, max_length=255)
    http_method: str = Field(min_length=1, max_length=10)
    request_headers: dict[str, Any] | None = None
    request_body: dict[str, Any] | None = None
    response_status: int = Field(ge=100, le=599)
    error_code: str | None = Field(default=None, max_length=100)
    error_message: str = Field(min_length=1)
    stack_trace: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class APIErrorLogUpdate(APIErrorLogCreate):
    pass


class APIErrorLogPatch(BaseModel):
    organization_id: int | None = None
    user_id: int | None = None
    endpoint: str | None = Field(default=None, min_length=1, max_length=255)
    http_method: str | None = Field(default=None, min_length=1, max_length=10)
    request_headers: dict[str, Any] | None = None
    request_body: dict[str, Any] | None = None
    response_status: int | None = Field(default=None, ge=100, le=599)
    error_code: str | None = Field(default=None, max_length=100)
    error_message: str | None = None
    stack_trace: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
