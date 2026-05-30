from fastcms import Resource

from enrichment.filters import EnrichedNewsFilter
from enrichment.model import NewsEnriched


class EnrichedNewsResource(Resource):
    model = NewsEnriched
    prefix = "/news-enriched"
    filter_class = EnrichedNewsFilter
    sort_fields = ["enriched_at"]  # noqa: RUF012
