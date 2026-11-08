from pydantic import BaseModel, Field 
from datetime import datetime
from uuid import UUID


class ExecutionSchema(BaseModel):
    """
    Schema for representing an execution instance.
    """

    execution_id: str = Field(
        description="Unique identifier for the execution"
    )
    user_id: UUID | None = Field(
        description="Unique identifier for the user associated with the execution" 
    )
    customer_id: str = Field(
        description="Unique identifier for the customer associated with the execution"
    )
    order_id: str = Field(
        description="Unique identifier for the order associated with the execution"
    )
    investigation_prompt: str = Field(
        description="The prompt or query that initiated the execution"
    )
    upfront_data: dict | None = Field(
        description="Any upfront data provided for the execution"
    )
    agent_result: dict | None = Field(
        description="The result produced by the agent during the execution"
    )
    recommender_result: dict | None = Field(
        description="The result produced by the recommender during the execution"
    )
    execution_success: bool | None = Field(
        description="Indicates whether the execution was successful"
    )
    execution_date: datetime = Field(
        description="The date and time when the execution occurred"
    )
    error_message: str | None = Field(
        description="Any error message associated with the execution"
    )