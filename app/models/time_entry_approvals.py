from datetime import datetime
from uuid import UUID

from sqlalchemy import (
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
from app.enums.time_entry_approval_status import TimeEntryApprovalStatus


class TimeEntryApproval(Base):
    __tablename__ = "time_entry_approvals"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    manual_time_entry_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "manual_time_entries.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    approved_by: Mapped[int | None] = mapped_column(
        INTEGER,
        nullable=True,
    )

    status: Mapped[TimeEntryApprovalStatus] = mapped_column(
        VARCHAR(20),
        nullable=False,
        server_default=text("'pending'"),
    )

    remarks: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
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