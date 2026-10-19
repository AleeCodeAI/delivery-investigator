from pydantic import BaseModel, Field
from datetime import date

class CustomerSchema(BaseModel):
    customer_id: str = Field(
        description="Unique identifier of the customer."
        )
    name: str = Field(
        description="Full name of the customer."
        )
    current_street: str = Field(
        description="Street address of the customer's current residence."
        )
    current_city: str = Field(
        description="City of the customer's current residence."
        )
    current_state: str = Field(
        description="State of the customer's current residence."
        )
    current_zip: str = Field(
        description="ZIP code of the customer's current residence."
        )
    account_created_at: date = Field(
        description="Date and time when the customer's account was created."
        )