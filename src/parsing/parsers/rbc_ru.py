import logging
from typing import ClassVar

import trafilatura
from bs4 import BeautifulSoup

from parsing.base import BaseSiteParser
from parsing.models import ParsedArticle

logger = logging.getLogger(__name__)


class RbcRuParser(BaseSiteParser):
    domains: ClassVar[list[str]] = ["rbc.ru", "www.rbc.ru"]

    async def parse(self, url: str, html: str) -> ParsedArticle:
        try:
            return self._extract(html)
        except Exception as exc:
            logger.warning("RbcRuParser failed for %s: %s, falling back to generic", url, exc)
            from parsing.generic import GenericParser

            return await GenericParser().parse(url, html)

    def _extract(self, html: str) -> ParsedArticle:
        soup = BeautifulSoup(html, "lxml")

        full_text: str | None = None
        article_el = soup.select_one("article.article__text")
        if article_el:
            full_text = article_el.get_text(separator="\n", strip=True)
        if not full_text:
            logger.debug("RbcRuParser: article.article__text not found, using trafilatura")
            full_text = trafilatura.extract(html, include_comments=False, include_tables=False)

        author: str | None = None
        author_el = soup.select_one(".article__authors")
        if author_el:
            author = author_el.get_text(strip=True)
        else:
            logger.debug("RbcRuParser: .article__authors not found")

        tags: list[str] | None = None
        tag_els = soup.select(".article__tags a")
        if tag_els:
            tags = [t.get_text(strip=True) for t in tag_els]
        else:
            logger.debug("RbcRuParser: .article__tags not found")

        categories: list[str] | None = None
        section_tag = soup.find("meta", property="article:section")
        if section_tag and section_tag.get("content"):
            categories = [section_tag["content"]]
        else:
            logger.debug("RbcRuParser: meta article:section not found")

        return ParsedArticle(
            full_text=full_text,
            author=author,
            tags=tags,
            categories=categories,
        )
