from datetime import datetime
from decimal import Decimal
from database.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Numeric, ForeignKey, CheckConstraint


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("customers.customer_id")
    )
    order_date: Mapped[datetime]
    sku: Mapped[str] = mapped_column(String(50))
    product_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    order_value: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    delivery_street: Mapped[str] = mapped_column(String(255))
    delivery_city: Mapped[str] = mapped_column(String(100))
    delivery_state: Mapped[str] = mapped_column(String(2))
    delivery_zip: Mapped[str] = mapped_column(String(10))
    order_status: Mapped[str] = mapped_column(String(50))
    fulfilled_from_warehouse_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("warehouses.warehouse_id")
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_order_quantity"),
        CheckConstraint("unit_price >= 0", name="chk_unit_price"),
        CheckConstraint("order_value >= 0", name="chk_order_value"),
        CheckConstraint("order_value = quantity * unit_price", name="chk_order_total"),
    )