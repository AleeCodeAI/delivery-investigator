from pydantic import BaseModel, Field
from datetime import date

class CustomerAddressHistorySchema(BaseModel):
    address_history_id: str = Field(
        description="Unique identifier of the customer address history record."
    )
    customer_id: str = Field(
        description="Unique identifier of the customer associated with this address."
    )
    street: str = Field(
        description="Street address recorded for the customer."
    )
    city: str = Field(
        description="City where the recorded address is located."
    )
    state: str = Field(
        description="Two-letter state code for the recorded address."
    )
    zip: str = Field(
        description="ZIP code of the recorded address."
    )
    effective_from: date = Field(
        description="Date when this address became effective for the customer."
    )
    effective_to: date | None = Field(
        description="Date when this address ceased to be effective, or None if it is still current."
    )