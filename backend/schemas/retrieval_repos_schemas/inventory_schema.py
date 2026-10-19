from pydantic import BaseModel, Field


class InventorySchema(BaseModel):
    inventory_id: str = Field(
        description="Unique identifier of the inventory record."
    )
    sku: str = Field(
        description="Stock keeping unit (SKU) identifying the product."
    )
    warehouse_id: str = Field(
        description="Unique identifier of the warehouse where the inventory is stored."
    )
    stock_quantity: int = Field(
        description="Current physical stock quantity of the product at the warehouse."
    )
    reserved_quantity: int = Field(
        description="Quantity of stock reserved for orders and not available for other orders."
    )