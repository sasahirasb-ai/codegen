from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class User_password(DeclarativeBase):
    __tablename__ = "user_password"

    id: Mapped[str] = mapped_column(
        String, length=40, nullable=False, primary_key=True, unique=True
    )
    user_id: Mapped[str] = mapped_column(String, length=40, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=datetime.utcnow
    )
