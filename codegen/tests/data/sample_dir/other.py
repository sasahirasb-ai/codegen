from pydantic import BaseModel, Field


class Other(BaseModel):
    id: int | None = Field(default=None, example=1)
    username: str | None = Field(default=None, example="johndoe")
