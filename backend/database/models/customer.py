from datetime import date
from database.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String

class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255))
    current_street: Mapped[str] = mapped_column(String(255))
    current_city: Mapped[str] = mapped_column(String(255))
    current_state: Mapped[str] = mapped_column(String(2))
    current_zip: Mapped[str] = mapped_column(String(10))
    account_created_at: Mapped[date]