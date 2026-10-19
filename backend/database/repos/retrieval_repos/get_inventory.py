from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Inventory
from schemas import InventorySchema


def get_inventory(sku: str) -> list[InventorySchema]:
    """
    Retrieve inventory records for a specific SKU across warehouses.

    Args:
        sku: The SKU of the product to retrieve inventory records for.

    Returns:
        A list of InventorySchema objects containing inventory IDs, SKU,
        warehouse IDs, stock quantities, and reserved quantities.

    Raises:
        LookupError: If no inventory records are found for the SKU.
    """
    with Session(engine) as session:
        statement = select(Inventory).where(
            Inventory.sku == sku
        )
        inventory_rows = session.scalars(statement).all()

        if not inventory_rows:
            raise LookupError(
                f"No inventory records found for SKU: {sku}"
            )

        return [
            InventorySchema(
                inventory_id=row.inventory_id,
                sku=row.sku,
                warehouse_id=row.warehouse_id,
                stock_quantity=row.stock_quantity,
                reserved_quantity=row.reserved_quantity,
            )
            for row in inventory_rows
        ]


if __name__ == "__main__":
    result = get_inventory(sku="SKU-HOME-2001")
    print(result)
