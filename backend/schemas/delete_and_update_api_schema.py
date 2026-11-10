from pydantic import BaseModel 
from uuid import UUID


class DeleteData(BaseModel):
    access_key: UUID
    email: str 


class UpdateData(BaseModel):
    user_id: UUID
    email: str