from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal
from uuid import UUID

class ProfileSchema(BaseModel):
    user_id: UUID = Field(
        description="Unique identifier of the user."
    )
    name: str | None = Field(
        description="Name of the user."
    )
    email: str = Field(
        description="Email address of the user."
    )
    role: Literal["admin", "operator"] = Field(
        description="Role of the user, either 'admin' or 'operator'."
    )
    created_at: datetime = Field(
        description="Timestamp when the user profile was created."
    )