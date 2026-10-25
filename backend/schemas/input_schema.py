from pydantic import BaseModel, Field


class InputDataSchema(BaseModel):
    """
    The schema for input data to the investigator
    """
    customer_id: str = Field(
        description="The unique customer id that purchased the order"
    )
    order_id: str = Field(
        description="Unique identifier for the order that was purchased"
    )
    investigation_prompt: str = Field(
        description="The investigation prompt for investigator provided by human operator"
    )