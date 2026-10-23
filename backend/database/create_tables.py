from database.models import (
    Customer,
    CustomerAddressHistory,
    Order,
    Shipment,
    ShipmentEvent,
    Inventory,
    InventoryEvent,
    Warehouse,
    Execution
)
from database.base import Base
from database.engine import engine

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()