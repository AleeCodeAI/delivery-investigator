from database.repos import get_inventory_events, get_inventory
from schemas import InventoryEventSchema, InventorySchema, FulfillmentEvidenceToolSchema


def fulfillment_evidence_tool(sku: str) -> FulfillmentEvidenceToolSchema:
    """
    Retrieve historical inventory events and current inventory data
    for a product to investigate potential fulfillment delays.

    Historical inventory events are primary sources of evidence regarding past 
    inventory movements, such as reservations or quality holds. The current 
    inventory snapshot is a supplementary source that provides additional context 
    about stock and reserved quantities.

    Args:
        sku (str): The unique SKU of the product being investigated.

    Returns:
        FulfillmentEvidenceToolSchema: An instance of the schema containing:
            - inventory_events (list[InventoryEventSchema]): Historical
              inventory events associated with the specified SKU.
            - inventory (InventorySchema): The current inventory snapshot
              for the specified SKU.

    Raises:
        RuntimeError: If an error occurs while retrieving inventory
            events or current inventory data. The original exception
            is preserved as the cause.
    """
    try:
        inventory_events: list[InventoryEventSchema] = get_inventory_events(
            sku=sku
        )
        inventory: InventorySchema | None = get_inventory(sku=sku)

        return FulfillmentEvidenceToolSchema(
                inventory_events=inventory_events,
                inventory=inventory
            )

    except Exception as exc:
        raise RuntimeError(
            f"Error occurred while retrieving fulfillment evidence "
            f"for SKU {sku}: {exc}"
        ) from exc