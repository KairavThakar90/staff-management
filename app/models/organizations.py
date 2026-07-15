from uuid import UUID

from sqlalchemy import CHAR, TEXT, TIMESTAMP, VARCHAR, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from datetime import datetime


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(
        VARCHAR(150),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        VARCHAR(150),
        unique=True,
        nullable=False,
    )

    logo_url: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    timezone: Mapped[str] = mapped_column(
        VARCHAR(100),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        CHAR(3),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        VARCHAR(20),
        nullable=False,
        server_default=text("'active'"),
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