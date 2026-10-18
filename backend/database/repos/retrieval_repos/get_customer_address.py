from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.engine import engine
from database.models import CustomerAddressHistory


def get_customer_address_history(customer_id: str) -> list[dict] | None:
    """
    Retrieve a customer's address history by their ID.

    Args:
        customer_id: The unique ID of the customer.

    Returns:
        A list of dictionaries containing the customer's address history,
        including address IDs, addresses, and their effective dates.
        Returns an empty list if no records are found.

    Raises:
        SQLAlchemyError: If a database operation fails.
    """
    try:
        with Session(engine) as session:
            statement = select(CustomerAddressHistory).where(
                CustomerAddressHistory.customer_id == customer_id
            )
            address_rows = session.scalars(statement).all()

            if not address_rows:
                return None

            return [
                {
                    "address_history_id": row.address_history_id,
                    "customer_id": row.customer_id,
                    "street": row.street,
                    "city": row.city,
                    "state": row.state,
                    "zip": row.zip,
                    "effective_from": str(row.effective_from),
                    "effective_to": (
                        str(row.effective_to) if row.effective_to else None
                    ),
                }
                for row in address_rows
            ]

    except SQLAlchemyError:
        raise


if __name__ == "__main__":
    result = get_customer_address_history(customer_id="CUST-189041")
    print(result)