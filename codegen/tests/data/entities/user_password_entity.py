from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from tests.data.entities.base_entity import Base


class User_passwordEntity(Base):
    __tablename__ = "user_password"

    id: Mapped[str] = mapped_column(
        String(40), nullable=False, primary_key=True, unique=True
    )
    user_id: Mapped[str] = mapped_column(String(40), nullable=False)
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=datetime.utcnow
    )
