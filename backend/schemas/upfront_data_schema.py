from pydantic import BaseModel, Field
from .retrieval_repos_schemas.customer_schema import CustomerSchema
from .retrieval_repos_schemas.order_schema import OrderSchema
from .retrieval_repos_schemas.shipment_schema import ShipmentSchema
from .retrieval_repos_schemas.shipment_events_schema import ShipmentEventSchema


class UpfrontDataSchema(BaseModel):
    """
    Schema representing upfront data for a shipment, including customer,
    order, shipment, and shipment events details.

    Attributes:
        customer: An instance of CustomerSchema containing customer details.
        order: An instance of OrderSchema containing order details.
        shipment: An instance of ShipmentSchema containing shipment details.
        shipment_events: A list of ShipmentEventsSchema instances containing
            shipment event details.
    """

    customer: CustomerSchema = Field(
        description="Customer details"
        )
    order: OrderSchema = Field(
        description="Order details"
        )
    shipment: ShipmentSchema | None= Field(
        description="Shipment details"
        )
    shipment_events: list[ShipmentEventSchema] | None = Field(
        description="List of shipment events"
        )