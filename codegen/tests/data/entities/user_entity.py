from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from tests.data.entities.base_entity import Base


class UserEntity(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(
        String(40), nullable=False, primary_key=True, unique=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=datetime.utcnow
    )
