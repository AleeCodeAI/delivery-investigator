from datetime import datetime
from database.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, ForeignKey


class InventoryEvent(Base):
    __tablename__ = "inventory_events"

    event_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    sku: Mapped[str] = mapped_column(String(50))
    warehouse_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("warehouses.warehouse_id")
    )
    event_type: Mapped[str] = mapped_column(String(50))
    quantity_change: Mapped[int]
    event_timestamp: Mapped[datetime]
    related_order_id: Mapped[str | None] = mapped_column(
        String(20), ForeignKey("orders.order_id")
    )