import logging
from langfuse.decorators import observe

from database.repos import get_customer_address_history
from schemas import CustomerAddressHistorySchema

logger = logging.getLogger(__name__)

@observe(as_type="tool", name="customer_address_history_tool")
def customer_address_history_tool(customer_id: str) -> list[CustomerAddressHistorySchema]:
    """
    Retrieve the address history associated with a customer.

    Args:
        customer_id (str): The unique identifier of the customer whose
            address history should be retrieved.

    Returns:
        list[CustomerAddressHistorySchema]: A list of address history
            records for the specified customer, including their historical
            and current addresses when available.

    Raises:
        RuntimeError: If an error occurs while retrieving the customer's
            address history. The original exception is preserved as the cause.
    """
    logger.info(f"customer_address_history_tool called: customer_id={customer_id}")

    try:
        customer_address_history: list[CustomerAddressHistorySchema] = get_customer_address_history(customer_id=customer_id)

        logger.info(
                f"Retrieved {len(customer_address_history)} address history records "
                f"for customer_id={customer_id}"
            )

        return customer_address_history

    except Exception as exc:
        logger.exception(f"Failed to retrieve address history for customer_id={customer_id}")
        raise RuntimeError(
                f"Error occurred while fetching customer address history "
                f"for ID {customer_id}: {exc}"
            ) from exc


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    result = customer_address_history_tool(customer_id="CUST-189041")
    print(result)