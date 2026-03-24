from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from db import Base


class CustomStyle(Base):
    __tablename__ = "custom_styles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    # 显示名称，如 "微博文案"、"论文摘要"
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    # URL-safe 标识符，用作 style 字段值，如 "weibo"、"paper_abstract"
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    # Prompt 模板，必须包含 {content} 占位符
    description: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    # 简短描述
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
