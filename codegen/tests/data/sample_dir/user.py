from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: int | None = Field(default=None, example=1)
    username: str | None = Field(default=None, example="johndoe")
    email: EmailStr | None = Field(default=None, example="johndoe@example.com")
    is_active: bool | None = Field(default=None, example=True)
    created_at: datetime | None = Field(default=None, example="2024-01-01T12:00:00Z")
    updated_at: datetime | None = Field(default=None, example="2024-01-02T12:00:00Z")
