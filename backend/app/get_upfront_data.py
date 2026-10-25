import logging
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


def get_upfront_data(customer_id: str, order_id: str) -> UpfrontDataSchema | None:
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
        shipment, and optional shipment events. Returns None if retrieving
        or assembling the data fails; the error is logged.
    """
    try:
        customer: CustomerSchema = get_customer(customer_id=customer_id)
        order: OrderSchema = get_order(order_id=order_id)
        shipment: ShipmentSchema | None = get_shipment(
            order_id=order_id
        )

        shipment_events: list[ShipmentEventSchema] | None = None

        if shipment:
            shipment_events = get_shipment_events(
                shipment_id=shipment.shipment_id
            )

        return UpfrontDataSchema(
            customer=customer,
            order=order,
            shipment=shipment,
            shipment_events=shipment_events,
        )

    except Exception as e:
        logging.info(
            f"Failed to get upfront data \n"
            f"[Customer: {customer_id}] \n"
            f"[Order: {order_id}] \n"
            f"[Error: {str(e)}]"
        )

        return None
    
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