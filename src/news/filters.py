from fastcms import Filter


class NewsFilter(Filter):
    source_domain__eq: str | None = None
    published_at__gte: str | None = None
    published_at__lte: str | None = None
    enrichment_status__eq: str | None = None
    title__contains: str | None = None
    announce_text__contains: str | None = None
