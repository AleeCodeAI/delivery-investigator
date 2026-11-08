from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class InvitationSchema(BaseModel):
    access_key: UUID = Field(
        description="The unique access key for the invitation."
    )
    name: str = Field(
        description="The name of the person being invited."
    )
    email: str = Field(
        description="The email address of the person being invited."
    )
    created_at: datetime = Field(
        description="The timestamp when the invitation was created."
    )