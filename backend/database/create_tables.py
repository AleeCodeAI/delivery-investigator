from database.models import (
    Customer,
    CustomerAddressHistory,
    Order,
    Shipment,
    ShipmentEvent,
    Inventory,
    InventoryEvent,
    Warehouse,
    Execution,
    Profile,
    Invitation
)

from database.models.users import auth_users
from database.base import Base
from database.engine import engine


def create_tables():
    tables = [
        table
        for table in Base.metadata.sorted_tables
        if table.schema != "auth"
    ]

    Base.metadata.create_all(bind=engine, tables=tables)


if __name__ == "__main__":
    create_tables()