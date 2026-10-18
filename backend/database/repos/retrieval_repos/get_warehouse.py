from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.engine import engine
from database.models import Warehouse


def get_warehouse(warehouse_id: str) -> dict | None:
    """
    Retrieve warehouse details by warehouse ID.

    Args:
        warehouse_id: The unique ID of the warehouse to retrieve.

    Returns:
        A dictionary containing the warehouse's ID, name, city, and state.
        Returns None if no matching warehouse is found.

    Raises:
        SQLAlchemyError: If a database operation fails.
    """
    try:
        with Session(engine) as session:
            statement = select(Warehouse).where(
                Warehouse.warehouse_id == warehouse_id
            )
            warehouse_row = session.scalars(statement).one_or_none()

            if warehouse_row is None:
                return None

            return {
                "warehouse_id": warehouse_row.warehouse_id,
                "name": warehouse_row.name,
                "city": warehouse_row.city,
                "state": warehouse_row.state,
            }

    except SQLAlchemyError:
        raise


if __name__ == "__main__":
    result = get_warehouse(warehouse_id="WH-5")
    print(result)