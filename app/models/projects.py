from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    BOOLEAN,
    DATE,
    INTEGER,
    TEXT,
    TIMESTAMP,
    VARCHAR,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.enums.project_status import ProjectStatus


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    project_name: Mapped[str] = mapped_column(
        VARCHAR(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    status: Mapped[ProjectStatus] = mapped_column(
        VARCHAR(20),
        nullable=False,
        server_default=text("'planning'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        DATE,
        nullable=True,
    )

    is_billable: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default=text("true"),
    )

    is_active: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default=text("true"),
    )

    created_by: Mapped[int | None] = mapped_column(
        INTEGER,
        nullable=True,
    )