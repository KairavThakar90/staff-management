from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    BOOLEAN,
    DATE,
    INTEGER,
    NUMERIC,
    TEXT,
    TIMESTAMP,
    VARCHAR,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.enums.task_status import TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    
    parent_task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
    )

    assigned_to: Mapped[int | None] = mapped_column(
        INTEGER,
        nullable=True,
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

    created_by: Mapped[int | None] = mapped_column(
        INTEGER,
        nullable=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        DATE,
        nullable=True,
    )

    due_date: Mapped[date | None] = mapped_column(
        DATE,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    estimated_hours: Mapped[Decimal | None] = mapped_column(
        NUMERIC(5, 2),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default=text("true"),
    )