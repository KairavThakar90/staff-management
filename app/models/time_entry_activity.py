from datetime import datetime, UTC

from sqlalchemy import (
    BIGINT,
    CheckConstraint,
    ForeignKey,
    Identity,
    INTEGER,
    SMALLINT,
    TIMESTAMP,
    text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TimeEntryActivity(Base):
    __tablename__ = "time_entry_activity"
    __table_args__ = (
        CheckConstraint(
            "((activity_percentage >= 0) AND (activity_percentage <= 100))",
            name="time_entry_activity_activity_percentage_check",
        ),
        Index("idx_time_entry_activity_entry", "time_entry_id"),
        Index("idx_time_entry_activity_org", "organization_id"),
        Index("idx_time_entry_activity_recorded", "recorded_at"),
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

    time_entry_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("time_entries.id", ondelete="CASCADE"),
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    keyboard_strokes: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        server_default=text("0"),
    )

    mouse_clicks: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        server_default=text("0"),
    )

    mouse_movements: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        server_default=text("0"),
    )

    activity_percentage: Mapped[int] = mapped_column(
        SMALLINT,
        nullable=False,
        server_default=text("0"),
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
