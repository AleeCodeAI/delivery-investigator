from pydantic import BaseModel, Field
from .retrieval_repos_schemas.inventory_events_schema import InventoryEventSchema
from .retrieval_repos_schemas.inventory_schema import InventorySchema


class FulfillmentEvidenceToolSchema(BaseModel):
    """
    Schema representing historical fulfillment evidence and
    supplementary inventory data.

    Attributes:
        inventory_events: Historical inventory events associated
            with the specified SKU.
        inventory: Inventory records across warehouses, or None
            if no inventory records are available.
    """

    inventory_events: list[InventoryEventSchema] = Field(
        description="Historical inventory events associated with the SKU."
    )
    inventory: list[InventorySchema] | None = Field(
        description="Current inventory records across warehouses, or None "
                    "if no records are available."
    )