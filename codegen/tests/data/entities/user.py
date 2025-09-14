from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class User(DeclarativeBase):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(
        String, length=40, nullable=False, primary_key=True, unique=True
    )
    name: Mapped[str] = mapped_column(String, length=100, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=datetime.utcnow
    )
