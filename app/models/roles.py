from datetime import datetime
from uuid import UUID

from sqlalchemy import BOOLEAN, TEXT, TIMESTAMP, VARCHAR, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Role(Base):
    __tablename__ = "roles"

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

    role_name: Mapped[str] = mapped_column(
        VARCHAR(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    is_system_role: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        server_default=text("false"),
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