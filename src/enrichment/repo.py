from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from enrichment.job_model import EnrichmentJob, JobStatus
from enrichment.model import NewsEnriched
from parsing.models import ParsedArticle


async def upsert_enriched(
    news_id: int, data: ParsedArticle, session: AsyncSession
) -> NewsEnriched:
    stmt = (
        insert(NewsEnriched)
        .values(
            news_id=news_id,
            full_text=data.full_text,
            images=data.images,
            categories=data.categories,
            tags=data.tags,
            author=data.author,
            views_count=data.views_count,
            comments_count=data.comments_count,
            keywords=data.keywords,
            summary=data.summary,
            region=data.region,
            has_video=data.has_video,
            extra_meta=data.extra_meta,
        )
        .on_conflict_do_update(
            index_elements=["news_id"],
            set_=dict(
                full_text=data.full_text,
                images=data.images,
                categories=data.categories,
                tags=data.tags,
                author=data.author,
                views_count=data.views_count,
                comments_count=data.comments_count,
                keywords=data.keywords,
                summary=data.summary,
                region=data.region,
                has_video=data.has_video,
                extra_meta=data.extra_meta,
                enriched_at=datetime.now(UTC),
            ),
        )
        .returning(NewsEnriched)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_enriched_by_news_id(news_id: int, session: AsyncSession) -> NewsEnriched | None:
    result = await session.execute(select(NewsEnriched).where(NewsEnriched.news_id == news_id))
    return result.scalar_one_or_none()


async def create_job(news_id: int, session: AsyncSession) -> EnrichmentJob:
    job = EnrichmentJob(news_id=news_id)
    session.add(job)
    await session.flush()
    await session.refresh(job)
    return job


async def get_pending_jobs(session: AsyncSession, limit: int = 10) -> list[EnrichmentJob]:
    result = await session.execute(
        select(EnrichmentJob)
        .where(EnrichmentJob.status == JobStatus.pending)
        .order_by(EnrichmentJob.created_at)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_job(job_id: int, session: AsyncSession) -> EnrichmentJob | None:
    result = await session.execute(select(EnrichmentJob).where(EnrichmentJob.id == job_id))
    return result.scalar_one_or_none()


async def get_jobs_by_status(
    status: JobStatus | None, session: AsyncSession
) -> list[EnrichmentJob]:
    q = select(EnrichmentJob).order_by(EnrichmentJob.created_at.desc())
    if status is not None:
        q = q.where(EnrichmentJob.status == status)
    result = await session.execute(q)
    return list(result.scalars().all())


async def update_job_status(
    job_id: int,
    status: JobStatus,
    session: AsyncSession,
    *,
    error: str | None = None,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
) -> None:
    values: dict = {"status": status}
    if error is not None:
        values["error"] = error
    if started_at is not None:
        values["started_at"] = started_at
    if finished_at is not None:
        values["finished_at"] = finished_at
    await session.execute(update(EnrichmentJob).where(EnrichmentJob.id == job_id).values(**values))
