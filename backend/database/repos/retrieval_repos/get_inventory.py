from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.engine import engine
from database.models import Inventory


def get_inventory(sku: str) -> list[dict] | None:
    """
    Retrieve inventory records for a specific SKU across warehouses.

    Args:
        sku: The SKU of the product to retrieve inventory records for.

    Returns:
        A list of dictionaries containing inventory IDs, SKU, warehouse IDs,
        stock quantities, and reserved quantities. Returns an empty list
        if no matching records are found.
    """
    try:
        with Session(engine) as session:
            statement = select(Inventory).where(
                Inventory.sku == sku
            )
            inventory_rows = session.scalars(statement).all()

            if not inventory_rows:
                return None

            return [
                {
                    "inventory_id": row.inventory_id,
                    "sku": row.sku,
                    "warehouse_id": row.warehouse_id,
                    "stock_quantity": row.stock_quantity,
                    "reserved_quantity": row.reserved_quantity,
                }
                for row in inventory_rows
            ]
    except SQLAlchemyError:
        raise

if __name__ == "__main__":
    result = get_inventory(sku="SKU-HOME-2001")
    print(result)