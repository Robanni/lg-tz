from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enrichment.model import NewsEnriched
from news.model import News
from shared.db import get_db

router = APIRouter(prefix="/news", tags=["News"])


class NewsCardResponse(BaseModel):
    id: int
    title: str
    source_url: str
    source_domain: str
    published_at: str
    announce_text: str | None
    enrichment_status: str
    full_text: str | None
    images: dict | None
    categories: list[str] | None
    tags: list[str] | None
    author: str | None
    views_count: int | None
    comments_count: int | None
    keywords: list[str] | None
    summary: str | None
    region: str | None
    has_video: bool | None
    extra_meta: dict | None
    enriched_at: str | None

    model_config = {"from_attributes": True}


class NewsSearchItem(BaseModel):
    id: int
    title: str
    source_url: str
    source_domain: str
    published_at: str
    announce_text: str | None
    enrichment_status: str

    model_config = {"from_attributes": True}


@router.get("/{news_id}/card", response_model=NewsCardResponse)
async def get_news_card(
    news_id: int,
    session: AsyncSession = Depends(get_db),
) -> NewsCardResponse:
    stmt = (
        select(News, NewsEnriched)
        .outerjoin(NewsEnriched, NewsEnriched.news_id == News.id)
        .where(News.id == news_id)
    )
    row = (await session.execute(stmt)).first()
    if not row:
        raise HTTPException(status_code=404, detail="News not found")

    news: News = row[0]
    enriched: NewsEnriched | None = row[1]
    return NewsCardResponse(
        id=news.id,
        title=news.title,
        source_url=news.source_url,
        source_domain=news.source_domain,
        published_at=news.published_at.isoformat(),
        announce_text=news.announce_text,
        enrichment_status=news.enrichment_status.value,
        full_text=enriched.full_text if enriched else None,
        images=enriched.images if enriched else None,
        categories=enriched.categories if enriched else None,
        tags=enriched.tags if enriched else None,
        author=enriched.author if enriched else None,
        views_count=enriched.views_count if enriched else None,
        comments_count=enriched.comments_count if enriched else None,
        keywords=enriched.keywords if enriched else None,
        summary=enriched.summary if enriched else None,
        region=enriched.region if enriched else None,
        has_video=enriched.has_video if enriched else None,
        extra_meta=enriched.extra_meta if enriched else None,
        enriched_at=enriched.enriched_at.isoformat() if enriched else None,
    )
