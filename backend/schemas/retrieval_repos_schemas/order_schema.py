from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class OrderSchema(BaseModel):
    order_id: str = Field(
        description="Unique identifier of the order."
    )
    customer_id: str = Field(
        description="Unique identifier of the customer who placed the order."
    )
    order_date: datetime = Field(
        description="Date and time when the order was placed."
    )
    sku: str = Field(
        description="Stock keeping unit (SKU) identifying the ordered product."
    )
    product_name: str = Field(
        description="Name of the product ordered by the customer."
    )
    quantity: int = Field(
        description="Number of units of the product included in the order."
    )
    unit_price: Decimal = Field(
        description="Price of a single unit of the product at the time of ordering."
    )
    order_value: Decimal = Field(
        description="Total order value, calculated as quantity multiplied by unit price."
    )
    delivery_street: str = Field(
        description="Street address where the order is intended to be delivered."
    )
    delivery_city: str = Field(
        description="City where the order is intended to be delivered."
    )
    delivery_state: str = Field(
        description="Two-letter state code of the order's delivery address."
    )
    delivery_zip: str = Field(
        description="ZIP code of the order's delivery address."
    )
    order_status: str = Field(
        description="Current status of the order, such as processing, shipped, or delivered."
    )
    fulfilled_from_warehouse_id: str = Field(
        description="Unique identifier of the warehouse assigned to fulfill the order."
    )