from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.engine import engine
from database.models import InventoryEvent


def get_inventory_events(sku: str) -> list[dict] | None:
    """
    Retrieve inventory events associated with a specific SKU.

    Args:
        sku: The SKU of the product to retrieve inventory events for.

    Returns:
        A list of dictionaries containing inventory event details,
        including event IDs, warehouse IDs, event types, quantity changes,
        timestamps, and related order IDs. Returns an empty list if no
        matching events are found.
    """
    try:
        with Session(engine) as session:
            statement = select(InventoryEvent).where(
                InventoryEvent.sku == sku
            )
            event_rows = session.scalars(statement).all()

            if not event_rows:
                return None

            return [
                {
                    "event_id": row.event_id,
                    "sku": row.sku,
                    "warehouse_id": row.warehouse_id,
                    "event_type": row.event_type,
                    "quantity_change": row.quantity_change,
                    "event_timestamp": str(row.event_timestamp),
                    "related_order_id": row.related_order_id,
                }
                for row in event_rows
            ]
    except SQLAlchemyError:
        raise

if __name__ == "__main__":
    result = get_inventory_events(sku="SKU-ELEC-1001")
    print(len(result))
    print(result)