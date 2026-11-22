from pydantic import BaseModel, EmailStr, Field

class SignUpData(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # 72 is Supabase's limit
    access_key: str = Field(min_length=1, max_length=100)