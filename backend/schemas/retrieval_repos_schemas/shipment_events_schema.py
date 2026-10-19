from datetime import datetime
from pydantic import BaseModel, Field


class ShipmentEventSchema(BaseModel):
    event_id: str = Field(
        description="Unique identifier of the shipment event."
    )
    shipment_id: str = Field(
        description="Unique identifier of the shipment associated with this event."
    )
    event_type: str = Field(
        description="Type of shipment event, such as shipment picked up, in transit, or delivered."
    )
    event_timestamp: datetime = Field(
        description="Date and time when the shipment event occurred."
    )
    location: str = Field(
        description="Location where the shipment event occurred."
    )
    description: str = Field(
        description="Detailed description of the shipment event and what happened."
    )