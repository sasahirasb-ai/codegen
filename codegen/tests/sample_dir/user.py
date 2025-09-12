from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class User(BaseModel):
    id: int | None = Field(None, example=1)
    username: str | None = Field(None, example='johndoe')
    email: EmailStr | None = Field(None, example='johndoe@example.com')
    is_active: bool | None = Field(None, example=True)
    created_at: datetime | None = Field(None, example='2024-01-01T12:00:00Z')
    updated_at: datetime | None = Field(None, example='2024-01-02T12:00:00Z')
