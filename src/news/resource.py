from fastcms import Resource

from news.filters import NewsFilter
from news.model import News


class NewsResource(Resource):
    model = News
    prefix = "/news"
    filter_class = NewsFilter
    sort_fields = ["published_at", "title", "source_domain"]  # noqa: RUF012

    async def after_create(self, obj, session, request) -> None:
        pass
