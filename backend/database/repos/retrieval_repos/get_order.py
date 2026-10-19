from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Order
from schemas import OrderSchema


def get_order(order_id: str) -> OrderSchema:
    """
    Retrieve an order's details by its ID.

    Args:
        order_id: The unique ID of the order to retrieve.

    Returns:
        An OrderSchema object containing the order's details, including
        customer, product, pricing, delivery address, status, and
        fulfillment warehouse.

    Raises:
        LookupError: If the order is not found.
    """
    with Session(engine) as session:
        statement = select(Order).where(
            Order.order_id == order_id
        )
        order_row = session.scalars(statement).one_or_none()

        if order_row is None:
            raise LookupError(f"Order: {order_id} not found.")

        return OrderSchema(
            order_id=order_row.order_id,
            customer_id=order_row.customer_id,
            order_date=order_row.order_date,
            sku=order_row.sku,
            product_name=order_row.product_name,
            quantity=order_row.quantity,
            unit_price=order_row.unit_price,
            order_value=order_row.order_value,
            delivery_street=order_row.delivery_street,
            delivery_city=order_row.delivery_city,
            delivery_state=order_row.delivery_state,
            delivery_zip=order_row.delivery_zip,
            order_status=order_row.order_status,
            fulfilled_from_warehouse_id=order_row.fulfilled_from_warehouse_id,
        )


if __name__ == "__main__":
    result = get_order(order_id="ORD-189001")
    print(result)
