from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import ShipmentEvent
from schemas import ShipmentEventSchema


def get_shipment_events(
    shipment_id: str,
) -> list[ShipmentEventSchema]:
    """
    Retrieve shipment events associated with a shipment ID.

    Args:
        shipment_id: The unique ID of the shipment.

    Returns:
        A list of ShipmentEventSchema objects containing shipment event
        details, including event IDs, event types, timestamps, locations,
        and descriptions.

    Raises:
        LookupError: If no shipment events are found for the shipment.
    """
    with Session(engine) as session:
        statement = select(ShipmentEvent).where(
            ShipmentEvent.shipment_id == shipment_id
        )
        event_rows = session.scalars(statement).all()

        if not event_rows:
            raise LookupError(
                f"No shipment events found for shipment: {shipment_id}"
            )

        return [
            ShipmentEventSchema(
                event_id=row.event_id,
                shipment_id=row.shipment_id,
                event_type=row.event_type,
                event_timestamp=row.event_timestamp,
                location=row.location,
                description=row.description,
            )
            for row in event_rows
        ]


if __name__ == "__main__":
    result = get_shipment_events(shipment_id="SHIP-189001")
    print(result)