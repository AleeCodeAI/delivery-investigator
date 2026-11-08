from datetime import datetime
import uuid

from sqlalchemy import String, Boolean, DateTime, UUID, func, text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Invitation(Base):
    __tablename__ = "invitations"

    access_key: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)

    status: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )