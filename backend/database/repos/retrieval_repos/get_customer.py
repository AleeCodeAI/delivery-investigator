from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.engine import engine
from database.models import Customer


def get_customer(customer_id: str) -> dict | None:
    """
    Retrieve a customer's details by their ID.

    Args:
        customer_id: The unique ID of the customer to retrieve.

    Returns:
        A dictionary containing the customer's ID, name, current address,
        and account creation date, or None if the customer is not found.

    Raises:
        SQLAlchemyError: If a database operation fails.
    """
    try:
        with Session(engine) as session:
            statement = select(Customer).where(
                Customer.customer_id == customer_id
            )
            customer_row = session.scalars(statement).one_or_none()

            if customer_row is None:
                return None

            return {
                "customer_id": customer_row.customer_id,
                "name": customer_row.name,
                "current_street": customer_row.current_street,
                "current_city": customer_row.current_city,
                "current_state": customer_row.current_state,
                "current_zip": customer_row.current_zip,
                "account_created_at": str(customer_row.account_created_at),
            }

    except SQLAlchemyError:
        raise


if __name__ == "__main__":
    result = get_customer(customer_id="CUST-189001")
    print(result)