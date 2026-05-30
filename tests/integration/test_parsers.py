import logging
import sys

import pytest

sys.path.insert(0, "src")

import parsing.parsers  # noqa: F401
from parsing.fetcher import ArticleFetcher
from parsing.registry import registry

logger = logging.getLogger(__name__)

# Real article URLs — change if they go 404
RBC_URL = "https://pro.rbc.ru/demo/6a195c139a79473b68e936fa"
RIA_URL = "https://ria.ru/20260530/tramp-2095758108.html"
UNKNOWN_URL = "https://lenta.ru/articles/2026/05/25/nuclear/"


@pytest.fixture(scope="module")
def fetcher():
    return ArticleFetcher()


@pytest.mark.asyncio
async def test_rbc_parser(fetcher: ArticleFetcher) -> None:
    html = await fetcher.fetch(RBC_URL)
    parser = registry.get("rbc.ru")
    result = await parser.parse(RBC_URL, html)

    logger.info("RBC RESULT: %s", result.model_dump(exclude_none=True))

    assert result.full_text is not None, "full_text должен быть заполнен"
    assert len(result.full_text) > 100, "full_text слишком короткий"


@pytest.mark.asyncio
async def test_ria_parser(fetcher: ArticleFetcher) -> None:
    html = await fetcher.fetch(RIA_URL)
    parser = registry.get("ria.ru")
    result = await parser.parse(RIA_URL, html)

    logger.info("RIA RESULT: %s", result.model_dump(exclude_none=True))

    assert result.full_text is not None, "full_text должен быть заполнен"
    assert len(result.full_text) > 100, "full_text слишком короткий"


@pytest.mark.asyncio
async def test_generic_fallback(fetcher: ArticleFetcher) -> None:
    html = await fetcher.fetch(UNKNOWN_URL)
    parser = registry.get("lenta.ru")
    result = await parser.parse(UNKNOWN_URL, html)

    logger.info("GENERIC (lenta.ru) RESULT: %s", result.model_dump(exclude_none=True))
    logger.info("full_text length: %d", len(result.full_text) if result.full_text else 0)


@pytest.mark.asyncio
async def test_rbc_bad_html() -> None:
    parser = registry.get("rbc.ru")
    result = await parser.parse(
        "https://rbc.ru/fake", "<html><body>no selectors here</body></html>"
    )

    logger.info("RBC BAD HTML RESULT: %s", result.model_dump(exclude_none=True))

    assert result is not None
