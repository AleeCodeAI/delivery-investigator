from sqlalchemy import select
from sqlalchemy.orm import Session
from database.engine import engine
from database.models import Warehouse
from schemas import WarehouseSchema


def get_warehouse(warehouse_id: str) -> WarehouseSchema:
    """
    Retrieve warehouse details by warehouse ID.

    Args:
        warehouse_id: The unique ID of the warehouse to retrieve.

    Returns:
        A WarehouseSchema object containing the warehouse's ID, name,
        city, and state.

    Raises:
        LookupError: If the warehouse is not found.
    """
    with Session(engine) as session:
        statement = select(Warehouse).where(
            Warehouse.warehouse_id == warehouse_id
        )
        warehouse_row = session.scalars(statement).one_or_none()

        if warehouse_row is None:
            raise LookupError(
                f"Warehouse: {warehouse_id} not found."
            )

        return WarehouseSchema(
            warehouse_id=warehouse_row.warehouse_id,
            name=warehouse_row.name,
            city=warehouse_row.city,
            state=warehouse_row.state,
        )


if __name__ == "__main__":
    result = get_warehouse(warehouse_id="WH-5")
    print(result)