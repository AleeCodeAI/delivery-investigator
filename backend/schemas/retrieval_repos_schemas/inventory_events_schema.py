from datetime import datetime
from pydantic import BaseModel, Field


class InventoryEventSchema(BaseModel):
    event_id: str = Field(
        description="Unique identifier of the inventory event."
    )
    sku: str = Field(
        description="Stock keeping unit (SKU) identifying the product associated with the event."
    )
    warehouse_id: str = Field(
        description="Unique identifier of the warehouse where the inventory event occurred."
    )
    event_type: str = Field(
        description="Type of inventory event, such as a stock receipt, reservation, or adjustment."
    )
    quantity_change: int = Field(
        description="Change in inventory quantity caused by the event; positive values increase stock and negative values decrease it."
    )
    event_timestamp: datetime = Field(
        description="Date and time when the inventory event occurred."
    )
    related_order_id: str = Field(
        description="Identifier of the order associated with the event, or None if the event is not related to an order."
    )