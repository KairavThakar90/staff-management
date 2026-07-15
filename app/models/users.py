from datetime import datetime
from uuid import UUID

from sqlalchemy import BOOLEAN, TEXT, TIMESTAMP, VARCHAR, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

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

    first_name: Mapped[str] = mapped_column(
        VARCHAR(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        VARCHAR(100),
        nullable=False,
    )

    display_name: Mapped[str | None] = mapped_column(
        VARCHAR(200),
        nullable=True,
    )

    email: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )

    is_email_verified: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default=text("false"),
    )

    status: Mapped[str] = mapped_column(
        VARCHAR(30),
        nullable=False,
        server_default=text("'pending_verification'"),
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
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