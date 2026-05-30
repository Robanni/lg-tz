from pydantic import BaseModel


class ParsedArticle(BaseModel):
    full_text: str | None = None
    images: list[str] | None = None
    categories: list[str] | None = None
    tags: list[str] | None = None
    author: str | None = None
    views_count: int | None = None
    comments_count: int | None = None
    keywords: list[str] | None = None
    summary: str | None = None
    region: str | None = None
    has_video: bool | None = None
    extra_meta: dict | None = None
