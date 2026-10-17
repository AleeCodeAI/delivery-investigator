from datetime import datetime
from database.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, ForeignKey, CheckConstraint


class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    order_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("orders.order_id"), unique=True
    )
    carrier: Mapped[str] = mapped_column(String(100))
    tracking_number: Mapped[str] = mapped_column(String(100), unique=True)
    ship_date: Mapped[datetime]
    shipment_status: Mapped[str] = mapped_column(String(50))
    delivered_at: Mapped[datetime | None]
    delivery_confirmation: Mapped[str] = mapped_column(String(50))

    __table_args__ = (
        CheckConstraint(
            "delivered_at IS NULL OR delivered_at >= ship_date",
            name="chk_delivery_timestamp",
        ),
    )