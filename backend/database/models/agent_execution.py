from datetime import datetime
from database.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String, JSON, func, DateTime

class Execution(Base):
    __tablename__ = "executions"

    execution_id: Mapped[str] = mapped_column(primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("customers.customer_id")
    )
    order_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("orders.order_id")
    )
    investigation_prompt: Mapped[str] = mapped_column(String(255))

    upfront_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    agent_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommender_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    execution_success: Mapped[bool | None] = mapped_column(nullable=True)
    execution_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    error_message: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )