from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.engine import engine
from database.models import Shipment


def get_shipment(order_id: str) -> dict | None:
    """
    Retrieve shipment details associated with an order ID.

    Args:
        order_id: The unique ID of the order.

    Returns:
        A dictionary containing shipment details, including shipment ID,
        carrier, tracking number, shipping date, status, delivery timestamp,
        and delivery confirmation. Returns None if no shipment is found.

    Raises:
        SQLAlchemyError: If a database operation fails.
    """
    try:
        with Session(engine) as session:
            statement = select(Shipment).where(
                Shipment.order_id == order_id
            )
            shipment_row = session.scalars(statement).one_or_none()

            if shipment_row is None:
                return None

            return {
                "shipment_id": shipment_row.shipment_id,
                "order_id": shipment_row.order_id,
                "carrier": shipment_row.carrier,
                "tracking_number": shipment_row.tracking_number,
                "ship_date": str(shipment_row.ship_date),
                "shipment_status": shipment_row.shipment_status,
                "delivered_at": (
                    str(shipment_row.delivered_at)
                    if shipment_row.delivered_at is not None
                    else None
                ),
                "delivery_confirmation": shipment_row.delivery_confirmation,
            }

    except SQLAlchemyError:
        raise


if __name__ == "__main__":
    result = get_shipment(order_id="ORD-189001")
    print(result)