from datetime import datetime

from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    CheckConstraint,
    ForeignKey,
    Identity,
    INTEGER,
    TEXT,
    TIMESTAMP,
    VARCHAR,
    text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.enums.time_entry_status import TimeEntryStatus


class TimeEntry(Base):
    __tablename__ = "time_entries"
    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'stopped')",
            name="time_entries_status_check",
        ),
        Index("idx_time_entries_project", "project_id"),
        Index("idx_time_entries_start_time", "start_time"),
        Index("idx_time_entries_status", "status"),
        Index("idx_time_entries_task", "task_id"),
        Index("idx_time_entries_user", "user_id"),
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

    user_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
    )

    project_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    task_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
    )

    start_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    end_time: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    total_seconds: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        server_default=text("0"),
    )

    status: Mapped[TimeEntryStatus] = mapped_column(
        VARCHAR(20),
        nullable=False,
        server_default=text("'running'"),
    )

    is_manual: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default=text("false"),
    )

    is_billable: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default=text("true"),
    )

    description: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
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