from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enrichment import repo, service
from enrichment.job_model import EnrichmentJob, JobStatus
from news.model import News
from shared.db import get_db

router = APIRouter(prefix="/enrichment", tags=["Enrichment"])


class EnqueueBody(BaseModel):
    news_id: int | None = None
    news_ids: list[int] | None = None
    filter: dict | None = None


class JobOut(BaseModel):
    id: int
    news_id: int
    status: JobStatus
    attempts: int
    error: str | None
    created_at: str
    started_at: str | None
    finished_at: str | None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, job: EnrichmentJob) -> "JobOut":
        return cls(
            id=job.id,
            news_id=job.news_id,
            status=job.status,
            attempts=job.attempts,
            error=job.error,
            created_at=job.created_at.isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            finished_at=job.finished_at.isoformat() if job.finished_at else None,
        )


@router.post("/jobs", response_model=list[JobOut], status_code=status.HTTP_201_CREATED)
async def create_jobs(
    body: EnqueueBody,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[JobOut]:
    news_ids: list[int] = []

    if body.news_id is not None:
        news_ids = [body.news_id]
    elif body.news_ids:
        news_ids = body.news_ids
    elif body.filter:
        q = select(News.id)
        if source_domain := body.filter.get("source_domain"):
            q = q.where(News.source_domain == source_domain)
        result = await session.execute(q)
        news_ids = list(result.scalars().all())

    if not news_ids:
        raise HTTPException(status_code=400, detail="No news_ids resolved from request body")

    jobs = await service.enqueue_many(news_ids, session)
    return [JobOut.from_orm(j) for j in jobs]


@router.get("/jobs", response_model=list[JobOut])
async def list_jobs(
    session: Annotated[AsyncSession, Depends(get_db)],
    job_status: Annotated[JobStatus | None, Query(alias="status")] = None,
) -> list[JobOut]:
    jobs = await repo.get_jobs_by_status(job_status, session)
    return [JobOut.from_orm(j) for j in jobs]


@router.get("/jobs/{job_id}", response_model=JobOut)
async def get_job(
    job_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobOut:
    job = await repo.get_job(job_id, session)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut.from_orm(job)
