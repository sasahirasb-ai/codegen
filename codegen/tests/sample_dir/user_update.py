from pydantic import BaseModel, Field

class UserUpdate(BaseModel):
    username: str | None = Field(None, example='johndoe_new')
    hashed_password: str | None = Field(None, example='new_hashed_password_here')
    is_active: bool | None = Field(None, example=False)
