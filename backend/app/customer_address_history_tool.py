from database.repos import get_customer_address_history
from schemas import CustomerAddressHistorySchema


def customer_address_history_tool(customer_id: str):
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
    try:
        customer_address_history: list[CustomerAddressHistorySchema] = get_customer_address_history(customer_id=customer_id)
        return customer_address_history
    
    except Exception as exc:
        raise RuntimeError(
                f"Error occurred while fetching customer address history "
                f"for ID {customer_id}: {exc}"
            ) from exc


if __name__ == "__main__":
    result = customer_address_history_tool(customer_id="CUST-189041")
    print(result)
