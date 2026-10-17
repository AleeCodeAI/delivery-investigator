from datetime import datetime
from database.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Text, ForeignKey


class ShipmentEvent(Base):
    __tablename__ = "shipment_events"

    event_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    shipment_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("shipments.shipment_id")
    )
    event_type: Mapped[str] = mapped_column(String(50))
    event_timestamp: Mapped[datetime]
    location: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)