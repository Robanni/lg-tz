from fastcms import Filter


class EnrichedNewsFilter(Filter):
    region__eq: str | None = None
    has_video__eq: bool | None = None
    author__contains: str | None = None
