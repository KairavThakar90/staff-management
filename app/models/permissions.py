from datetime import datetime
from uuid import UUID

from sqlalchemy import TEXT, TIMESTAMP, VARCHAR, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    permission_name: Mapped[str] = mapped_column(
        VARCHAR(150),
        nullable=False,
        unique=True,
    )

    module: Mapped[str] = mapped_column(
        VARCHAR(100),
        nullable=False,
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