from datetime import datetime

from sqlalchemy import (
    BIGINT,
    CheckConstraint,
    ForeignKey,
    Identity,
    INTEGER,
    TEXT,
    TIMESTAMP,
    VARCHAR,
    Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TimeEntryAppUsage(Base):
    __tablename__ = "time_entry_app_usage"
    __table_args__ = (
        CheckConstraint(
            "(duration_seconds >= 0)",
            name="chk_app_usage_duration",
        ),
        Index("idx_time_entry_app_usage_app", "application_name"),
        Index("idx_time_entry_app_usage_entry", "time_entry_id"),
        Index("idx_time_entry_app_usage_org", "organization_id"),
        Index("idx_time_entry_app_usage_recorded", "recorded_at"),
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

    application_name: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
    )

    window_title: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    duration_seconds: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        server_default=text("0"),
    )

    recorded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
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
