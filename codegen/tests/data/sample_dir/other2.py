from pydantic import BaseModel, Field


class Other2(BaseModel):
    id: int | None = Field(default=None, example=1)
    username: str | None = Field(default=None, example="johndoe")
