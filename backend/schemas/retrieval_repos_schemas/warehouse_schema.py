from pydantic import BaseModel, Field


class WarehouseSchema(BaseModel):
    warehouse_id: str = Field(
        description="Unique identifier of the warehouse."
    )
    name: str = Field(
        description="Name of the warehouse."
    )
    city: str = Field(
        description="City where the warehouse is located."
    )
    state: str = Field(
        description="Two-letter state code of the warehouse's location."
    )