from sqlalchemy import String, Text, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from db import Base


class HistoryRecord(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(Text, nullable=False, default="")
    style: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
