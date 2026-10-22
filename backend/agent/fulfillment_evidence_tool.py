import logging

from database.repos import get_inventory_events, get_inventory
from schemas import InventoryEventSchema, InventorySchema, FulfillmentEvidenceToolSchema

logger = logging.getLogger(__name__)


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
            - inventory (list[InventorySchema] | None): The current inventory
              snapshot records for the specified SKU, or None if unavailable.

    Raises:
        RuntimeError: If an error occurs while retrieving inventory
            events or current inventory data. The original exception
            is preserved as the cause.
    """
    logger.info(f"fulfillment_evidence_tool called: sku={sku}")

    try:
        inventory_events: list[InventoryEventSchema] = get_inventory_events(sku=sku)
        logger.info(
            f"Retrieved {len(inventory_events)} inventory events for sku={sku}"
        )

        inventory: list[InventorySchema] | None = get_inventory(sku=sku)
        if inventory:
            logger.info(
                f"Retrieved {len(inventory)} inventory snapshot records for sku={sku}"
            )

        return FulfillmentEvidenceToolSchema(
                inventory_events=inventory_events,
                inventory=inventory
            )

    except Exception as exc:
        logger.exception(f"Failed to retrieve fulfillment evidence for sku={sku}")
        raise RuntimeError(
            f"Error occurred while retrieving fulfillment evidence "
            f"for SKU {sku}: {exc}"
        ) from exc


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    result = fulfillment_evidence_tool(sku="SKU-ELEC-1001")
    print(result.inventory_events)
    print(result.inventory)