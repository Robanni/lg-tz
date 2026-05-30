import logging
from typing import ClassVar

import trafilatura
from bs4 import BeautifulSoup

from parsing.base import BaseSiteParser
from parsing.models import ParsedArticle

logger = logging.getLogger(__name__)


class GenericParser(BaseSiteParser):
    domains: ClassVar[list[str]] = []

    async def parse(self, url: str, html: str) -> ParsedArticle:
        try:
            return self._extract(html)
        except Exception:
            logger.exception("GenericParser failed for %s", url)
            return ParsedArticle()

    def _extract(self, html: str) -> ParsedArticle:
        full_text = trafilatura.extract(html, include_comments=False, include_tables=False)
        if full_text is None:
            logger.warning("trafilatura returned None")

        soup = BeautifulSoup(html, "lxml")

        images: list[str] | None = None
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            images = [og_image["content"]]

        keywords: list[str] | None = None
        kw_tag = soup.find("meta", attrs={"name": "keywords"})
        if kw_tag and kw_tag.get("content"):
            keywords = [k.strip() for k in kw_tag["content"].split(",") if k.strip()]

        summary: str | None = None
        desc_tag = soup.find("meta", property="og:description")
        if desc_tag and desc_tag.get("content"):
            summary = desc_tag["content"]

        has_video = bool(soup.find("video"))

        return ParsedArticle(
            full_text=full_text,
            images=images,
            keywords=keywords,
            summary=summary,
            has_video=has_video,
        )
