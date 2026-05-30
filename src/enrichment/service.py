import asyncio
import logging
from datetime import UTC, datetime
from urllib.parse import urlparse

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from enrichment import repo
from enrichment.job_model import EnrichmentJob, JobStatus
from news.model import EnrichmentStatus, News
from parsing.fetcher import ArticleFetcher
from parsing.registry import registry

logger = logging.getLogger(__name__)

_fetcher = ArticleFetcher()


async def enqueue(news_id: int, session: AsyncSession) -> EnrichmentJob:
    job = await repo.create_job(news_id, session)
    await session.commit()
    logger.info("Enqueued job %d for news_id=%d", job.id, news_id)
    return job


async def enqueue_many(news_ids: list[int], session: AsyncSession) -> list[EnrichmentJob]:
    jobs = [await repo.create_job(nid, session) for nid in news_ids]
    await session.commit()
    logger.info("Enqueued %d jobs", len(jobs))
    return jobs


async def run_job(job_id: int, session: AsyncSession) -> None:
    job = await repo.get_job(job_id, session)
    if job is None or job.status != JobStatus.pending:
        return

    now = datetime.now(UTC)
    await repo.update_job_status(job_id, JobStatus.running, session, started_at=now)
    await session.execute(
        update(EnrichmentJob)
        .where(EnrichmentJob.id == job_id)
        .values(attempts=EnrichmentJob.attempts + 1)
    )
    await session.commit()

    news: News | None = (
        await session.execute(select(News).where(News.id == job.news_id))
    ).scalar_one_or_none()
    if news is None:
        await repo.update_job_status(
            job_id,
            JobStatus.failed,
            session,
            error="news row not found",
            finished_at=datetime.now(UTC),
        )
        await session.commit()
        return

    try:
        html = await _fetcher.fetch(news.source_url)
        domain = urlparse(news.source_url).netloc
        parser = registry.get(domain)
        try:
            article = await parser.parse(news.source_url, html)
        except Exception as exc:
            logger.warning(
                "Parser %s failed for %s: %s — falling back to generic",
                type(parser).__name__,
                news.source_url,
                exc,
            )
            from parsing.generic import GenericParser

            article = await GenericParser().parse(news.source_url, html)

        await repo.upsert_enriched(news.id, article, session)
        await session.execute(
            update(News).where(News.id == news.id).values(enrichment_status=EnrichmentStatus.done)
        )
        await repo.update_job_status(
            job_id, JobStatus.done, session, finished_at=datetime.now(UTC)
        )
        await session.commit()
        logger.info("Job %d done for news_id=%d", job_id, news.id)

    except Exception as exc:
        logger.error("Job %d failed: %s", job_id, exc, exc_info=True)
        await session.rollback()
        await repo.update_job_status(
            job_id,
            JobStatus.failed,
            session,
            error=str(exc),
            finished_at=datetime.now(UTC),
        )
        await session.execute(
            update(News)
            .where(News.id == job.news_id)
            .values(enrichment_status=EnrichmentStatus.failed)
        )
        await session.commit()


async def run_pending(session: AsyncSession, batch: int = 5) -> None:
    jobs = await repo.get_pending_jobs(session, limit=batch)
    if not jobs:
        return
    logger.info("Processing %d pending jobs", len(jobs))
    await asyncio.gather(*(run_job(j.id, session) for j in jobs))
