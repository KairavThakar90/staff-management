from datetime import date, datetime

from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    CheckConstraint,
    DATE,
    ForeignKey,
    Identity,
    INTEGER,
    TEXT,
    TIMESTAMP,
    VARCHAR,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.enums.project_status import ProjectStatus


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(
            "status IN ('planning', 'active', 'completed', 'cancelled')",
            name="projects_status_check",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        Identity(always=True),
        primary_key=True,
    )

    organization_id: Mapped[int] = mapped_column(
        BIGINT,
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

    start_date: Mapped[date | None] = mapped_column(
        DATE,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    is_billable: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default=text("true"),
    )

    time_tracked_seconds: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        server_default=text("0"),
    )

    created_by: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
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
