import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import ForeignKey, String, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        primary_key=True
    )

    name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    email: Mapped[str] = mapped_column(String(100), unique=True)

    role: Mapped[Literal["admin", "operator"]] = mapped_column(
        String(20),
        default="operator"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )