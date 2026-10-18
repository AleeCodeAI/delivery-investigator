from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.engine import engine
from database.models import ShipmentEvent


def get_shipment_events(shipment_id: str) -> list[dict] | None:
    """
    Retrieve shipment events associated with a shipment ID.

    Args:
        shipment_id: The unique ID of the shipment.

    Returns:
        A list of dictionaries containing shipment event details,
        including event IDs, event types, timestamps, locations, and
        descriptions. Returns an empty list if no records are found.

    Raises:
        SQLAlchemyError: If a database operation fails.
    """
    try:
        with Session(engine) as session:
            statement = select(ShipmentEvent).where(
                ShipmentEvent.shipment_id == shipment_id
            )
            event_rows = session.scalars(statement).all()

            if not event_rows:
                return None

            return [
                {
                    "event_id": row.event_id,
                    "shipment_id": row.shipment_id,
                    "event_type": row.event_type,
                    "event_timestamp": str(row.event_timestamp),
                    "location": row.location,
                    "description": row.description,
                }
                for row in event_rows
            ]

    except SQLAlchemyError:
        raise


if __name__ == "__main__":
    result = get_shipment_events(shipment_id="SHIP-189001")
    print(result)