from datetime import date, datetime
from decimal import Decimal


from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    CheckConstraint,
    DATE,
    ForeignKey,
    Identity,
    INTEGER,
    NUMERIC,
    TEXT,
    TIMESTAMP,
    VARCHAR,
    text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.enums.task_status import TaskStatus


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "((due_date IS NULL) OR (start_date IS NULL) OR (due_date >= start_date))",
            name="chk_tasks_dates",
        ),
        CheckConstraint(
            "((estimated_hours IS NULL) OR (estimated_hours >= 0))",
            name="tasks_estimated_hours_check",
        ),
        CheckConstraint(
            "status IN ('todo', 'in_progress', 'completed')",
            name="tasks_status_check",
        ),
        Index("idx_tasks_created_by", "created_by"),
        Index("idx_tasks_due_date", "due_date"),
        Index("idx_tasks_name", "task_name"),
        Index("idx_tasks_organization", "organization_id"),
        Index("idx_tasks_project", "project_id"),
        Index("idx_tasks_start_date", "start_date"),
        Index("idx_tasks_status", "status"),
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

    project_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    task_name: Mapped[str] = mapped_column(
        VARCHAR(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    status: Mapped[TaskStatus] = mapped_column(
        VARCHAR(20),
        nullable=False,
        server_default=text("'todo'"),
    )

    start_date: Mapped[date | None] = mapped_column(
        DATE,
        nullable=True,
    )

    due_date: Mapped[date | None] = mapped_column(
        DATE,
        nullable=True,
    )

    estimated_hours: Mapped[Decimal | None] = mapped_column(
        NUMERIC(5, 2),
        nullable=True,
    )

    time_tracked_seconds: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        server_default=text("0"),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    completed_by: Mapped[int | None] = mapped_column(
        BIGINT,
        nullable=True,
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
