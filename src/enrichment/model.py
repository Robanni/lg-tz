from datetime import datetime

from sqlalchemy import ARRAY, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from shared.base import Base


class NewsEnriched(Base):
    __tablename__ = "news_enriched"

    id: Mapped[int] = mapped_column(primary_key=True)
    news_id: Mapped[int] = mapped_column(
        ForeignKey("news.id", ondelete="CASCADE"), unique=True, index=True
    )

    full_text: Mapped[str | None] = mapped_column(Text)
    images: Mapped[dict | None] = mapped_column(JSONB)
    categories: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    author: Mapped[str | None] = mapped_column(String(255))
    views_count: Mapped[int | None] = mapped_column(Integer)
    comments_count: Mapped[int | None] = mapped_column(Integer)
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    summary: Mapped[str | None] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(String(255))
    has_video: Mapped[bool | None]
    extra_meta: Mapped[dict | None] = mapped_column(JSONB)
    enriched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
