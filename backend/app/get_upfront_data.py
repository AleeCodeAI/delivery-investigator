from database.repos import (
        get_customer,
        get_order,
        get_shipment,
        get_shipment_events,
    )
from schemas import (
        UpfrontDataSchema,
        CustomerSchema,
        OrderSchema,
        ShipmentSchema,
        ShipmentEventSchema,
    )


def get_upfront_data(customer_id: str,order_id: str) -> UpfrontDataSchema:
    """
    Retrieve the primary data required for a delivery investigation.

    Fetches the customer and order records, followed by the associated
    shipment and its events if a shipment exists. Customer and order
    records are required, while shipment data is optional.

    Args:
        customer_id: ID of the customer being investigated.
        order_id: ID of the order being investigated.

    Returns:
        An UpfrontDataSchema containing the customer, order, optional
        shipment, and optional shipment events.

    Raises:
        RuntimeError: If retrieving or assembling the upfront data fails.
            The original exception is preserved as the cause.
    """
    try:
        customer: CustomerSchema = get_customer(customer_id=customer_id)
        order: OrderSchema = get_order(order_id=order_id)
        shipment: ShipmentSchema | None = get_shipment(
            order_id=order_id
        )

        shipment_events = None

        if shipment:
            shipment_events: list[ShipmentEventSchema] = get_shipment_events(
                shipment_id=shipment.shipment_id
            )

        return UpfrontDataSchema(
            customer=customer,
            order=order,
            shipment=shipment,
            shipment_events=shipment_events,
        )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to retrieve upfront data for customer "
            f"{customer_id!r} and order {order_id!r}. "
            f"Original error: {exc}"
        ) from exc

if __name__ == "__main__":
    upfrontdata: UpfrontDataSchema = get_upfront_data(
        customer_id="CUST-189012",
        order_id="ORD-189001"
    )
    print(
        f"""
        UPFRONT DATA RECEIVED:
        Customer: 
        {upfrontdata.customer.model_dump()}
        Order:
        {upfrontdata.order.model_dump()}
        Shipment:
        {upfrontdata.shipment.model_dump() if upfrontdata.shipment else "No shipment found."}
        Shipment Events:
        {
            [event.model_dump() for event in upfrontdata.shipment_events]
            if upfrontdata.shipment_events
            else "No shipment events found."
        }
        """
    )