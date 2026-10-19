from datetime import datetime
from pydantic import BaseModel, Field


class ShipmentSchema(BaseModel):
    shipment_id: str = Field(
        description="Unique identifier of the shipment."
    )
    order_id: str = Field(
        description="Unique identifier of the order associated with this shipment."
    )
    carrier: str = Field(
        description="Name of the shipping carrier responsible for transporting the shipment."
    )
    tracking_number: str = Field(
        description="Tracking number used to track the shipment with the carrier."
    )
    ship_date: datetime = Field(
        description="Date and time when the shipment was dispatched."
    )
    shipment_status: str = Field(
        description="Current status of the shipment, such as in transit or delivered."
    )
    delivered_at: datetime | None = Field(
        description="Date and time when the shipment was delivered, or None if it has not been delivered."
    )
    delivery_confirmation: str = Field(
        description="Delivery confirmation status indicating whether and how the delivery was confirmed."
    )