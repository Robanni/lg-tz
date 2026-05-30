from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from parsing.base import BaseSiteParser


class ParserRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, BaseSiteParser] = {}
        self._generic: BaseSiteParser | None = None

    def register(self, parser_cls: type[BaseSiteParser]) -> None:
        instance = parser_cls()
        for domain in parser_cls.domains:
            self._registry[domain] = instance

    def get(self, domain: str) -> BaseSiteParser:
        if domain in self._registry:
            return self._registry[domain]
        if self._generic is None:
            from parsing.generic import GenericParser

            self._generic = GenericParser()
        return self._generic


registry = ParserRegistry()
