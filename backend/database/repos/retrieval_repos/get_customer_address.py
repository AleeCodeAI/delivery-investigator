from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import CustomerAddressHistory
from schemas import CustomerAddressHistorySchema


def get_customer_address_history(customer_id: str) -> list[CustomerAddressHistorySchema]:
    """
    Retrieve a customer's address history by their ID.

    Args:
        customer_id: The unique ID of the customer.

    Returns:
        A list of CustomerAddressHistorySchema objects containing the
        customer's address history, including address IDs, addresses,
        and their effective dates.

    Raises:
        LookupError: If the customer has no address history records.
    """
    with Session(engine) as session:
        statement = select(CustomerAddressHistory).where(
            CustomerAddressHistory.customer_id == customer_id
        )
        address_rows = session.scalars(statement).all()

        if not address_rows:
            raise LookupError(
                f"No address history found for customer: {customer_id}"
            )

        return [
            CustomerAddressHistorySchema(
                address_history_id=row.address_history_id,
                customer_id=row.customer_id,
                street=row.street,
                city=row.city,
                state=row.state,
                zip=row.zip,
                effective_from=row.effective_from,
                effective_to=row.effective_to,
            )
            for row in address_rows
        ]


if __name__ == "__main__":
    result = get_customer_address_history(customer_id="CUST-189041")
    print(result)
