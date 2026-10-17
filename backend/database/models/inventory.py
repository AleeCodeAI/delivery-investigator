from database.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, ForeignKey, CheckConstraint, UniqueConstraint


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    sku: Mapped[str] = mapped_column(String(50))
    warehouse_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("warehouses.warehouse_id")
    )
    stock_quantity: Mapped[int]
    reserved_quantity: Mapped[int]

    __table_args__ = (
        UniqueConstraint("sku", "warehouse_id", name="uq_inventory_sku_warehouse"),
        CheckConstraint("stock_quantity >= 0", name="chk_stock_quantity"),
        CheckConstraint("reserved_quantity >= 0", name="chk_reserved_quantity"),
    )