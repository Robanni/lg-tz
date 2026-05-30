import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.base import Base


class EnrichmentStatus(enum.StrEnum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(512))
    source_url: Mapped[str] = mapped_column(String(2048), unique=True)
    source_domain: Mapped[str] = mapped_column(String(255), index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    announce_text: Mapped[str | None] = mapped_column(Text)
    enrichment_status: Mapped[EnrichmentStatus] = mapped_column(
        Enum(EnrichmentStatus, name="enrichmentstatus"),
        default=EnrichmentStatus.pending,
        server_default=EnrichmentStatus.pending.value,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
