from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import InventoryEvent
from schemas import InventoryEventSchema


def get_inventory_events(sku: str) -> list[InventoryEventSchema]:
    """
    Retrieve inventory events associated with a specific SKU.

    Args:
        sku: The SKU of the product to retrieve inventory events for.

    Returns:
        A list of InventoryEventSchema objects containing inventory event
        details, including event IDs, warehouse IDs, event types, quantity
        changes, timestamps, and related order IDs.

    Raises:
        LookupError: If no inventory events are found for the SKU.
    """
    with Session(engine) as session:
        statement = select(InventoryEvent).where(
            InventoryEvent.sku == sku
        )
        event_rows = session.scalars(statement).all()

        if not event_rows:
            raise LookupError(
                f"No inventory events found for SKU: {sku}"
            )

        return [
            InventoryEventSchema(
                event_id=row.event_id,
                sku=row.sku,
                warehouse_id=row.warehouse_id,
                event_type=row.event_type,
                quantity_change=row.quantity_change,
                event_timestamp=row.event_timestamp,
                related_order_id=row.related_order_id,
            )
            for row in event_rows
        ]


if __name__ == "__main__":
    result = get_inventory_events(sku="SKU-ELEC-1001")
    print(len(result))
    print(result)
