from pydantic import BaseModel


class InsertInvitationData(BaseModel):
    name: str
    email: str