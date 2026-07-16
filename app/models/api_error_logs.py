from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import BIGINT, Index, Identity, SMALLINT, TEXT, TIMESTAMP, VARCHAR, text
from sqlalchemy.dialects.postgresql import JSONB, INET, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class APIErrorLog(Base):
    __tablename__ = "api_error_logs"
    __table_args__ = (
        Index("idx_api_error_logs_created", "created_at"),
        Index("idx_api_error_logs_endpoint", "endpoint"),
        Index("idx_api_error_logs_org", "organization_id"),
        Index("idx_api_error_logs_request", "request_id"),
        Index("idx_api_error_logs_status", "response_status"),
        Index("idx_api_error_logs_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        Identity(always=True),
        primary_key=True,
    )

    organization_id: Mapped[int | None] = mapped_column(
        BIGINT,
        nullable=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        BIGINT,
        nullable=True,
    )

    request_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        server_default=text("gen_random_uuid()"),
    )

    endpoint: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
    )

    http_method: Mapped[str] = mapped_column(
        VARCHAR(10),
        nullable=False,
    )

    request_headers: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    request_body: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    response_status: Mapped[int] = mapped_column(
        SMALLINT,
        nullable=False,
    )

    error_code: Mapped[str | None] = mapped_column(
        VARCHAR(100),
        nullable=True,
    )

    error_message: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )

    stack_trace: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        INET,
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
