from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Customer
from schemas import CustomerSchema


def get_customer(customer_id: str) -> CustomerSchema:
    """
    Retrieve a customer's details by their ID.

    Args:
        customer_id: The unique ID of the customer to retrieve.

    Returns:
        A CustomerSchema object containing the customer's details.

    Raises:
        LookupError: If the customer is not found.
    """
    with Session(engine) as session:
        statement = select(Customer).where(
            Customer.customer_id == customer_id
        )
        customer_row = session.scalars(statement).one_or_none()

        if customer_row is None:
            raise LookupError(f"Customer: {customer_id} not found.")

        return CustomerSchema(
            customer_id=customer_row.customer_id,
            name=customer_row.name,
            current_street=customer_row.current_street,
            current_city=customer_row.current_city,
            current_state=customer_row.current_state,
            current_zip=customer_row.current_zip,
            account_created_at=customer_row.account_created_at,
        )


if __name__ == "__main__":
    result = get_customer(customer_id="CUST-189001")
    print(result)
