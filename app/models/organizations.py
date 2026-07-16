from datetime import datetime

from sqlalchemy import BIGINT, CHAR, CheckConstraint, Index, TEXT, TIMESTAMP, VARCHAR, Identity, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.enums.organization_status import OrganizationStatus


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'trial', 'inactive', 'suspended')",
            name="organizations_status_check",
        ),
        Index("idx_organizations_name", "name"),
        Index("idx_organizations_status", "status"),
    )

    id: Mapped[int] = mapped_column(
        BIGINT,
        Identity(always=True),
        primary_key=True,
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

    status: Mapped[OrganizationStatus] = mapped_column(
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