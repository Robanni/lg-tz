from abc import ABC, abstractmethod

from parsing.models import ParsedArticle


class BaseSiteParser(ABC):
    domains: list[str]

    @abstractmethod
    async def parse(self, url: str, html: str) -> ParsedArticle: ...
