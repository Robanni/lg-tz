"""Seed script — inserts real news rows.

Idempotent: skips if news table already has rows.
Run: python scripts/seed.py
"""

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from news.model import EnrichmentStatus, News
from shared.db import SessionLocal

# ruff: noqa
# fmt: off
SEED_DATA: list[dict] = [
    # rbc.ru
    {
        "title": "Суд в Москве арестовал мужчину за подготовку к подрыву здания Минюста",
        "source_domain": "rbc.ru",
        "source_url": "https://www.rbc.ru/society/30/05/2026/6a1b28559a794793c1a108f0",
        "announce_text": "Столичный суд арестовал мужчину по делу о приготовлении к незаконному изготовлению взрывного устройства для подрыва здания Министерства юстиции РФ.",  # noqa: RUF001
    },
    {
        "title": "Сафонов стал первым россиянином, дважды выигравшим Лигу чемпионов",
        "source_domain": "rbc.ru",
        "source_url": "https://www.rbc.ru/sport/30/05/2026/6a196aaf9a79471620dd9593",
        "announce_text": "Голкипер «Пари Сен-Жермен» Матвей Сафонов стал первым двукратным победителем Лиги чемпионов среди россиян. ПСЖ в финале обыграл лондонский «Арсенал».",
    },
    {
        "title": "Welt узнал о планах США быстрее ожидаемого вывести часть войск из Европы",
        "source_domain": "rbc.ru",
        "source_url": "https://www.rbc.ru/politics/30/05/2026/6a1b211d9a7947300e1ffa79",
        "announce_text": "США в ближайшие недели представят НАТО план сокращения военного присутствия в Европе. Вашингтон хочет усилить передачу основной ответственности за оборону континента европейским союзникам.",
    },
    {
        "title": "NYT узнала о проекте соглашения США и Ирана с фондом в $300 млрд",
        "source_domain": "rbc.ru",
        "source_url": "https://www.rbc.ru/politics/30/05/2026/6a1b18729a7947b6179807b2",
        "announce_text": "Проект соглашения между США и Ираном предусматривает создание совместного фонда объёмом $300 млрд для поддержки иранской экономики.",
    },
    {
        "title": "Стал известен лучший игрок финала Лиги чемпионов",
        "source_domain": "rbc.ru",
        "source_url": "https://www.rbc.ru/sport/30/05/2026/6a1b393d9a79473775250d07",
        "announce_text": "По итогам финала Лиги чемпионов в Будапеште UEFA назвал лучшего игрока матча.",
    },
    {
        "title": "Медведев пригрозил ударом по АЭС на Украине и в НАТО из-за атаки на ЗАЭС",
        "source_domain": "rbc.ru",
        "source_url": "https://www.rbc.ru/politics/30/05/2026/6a1b38579a79473775250d03",
        "announce_text": "Заместитель председателя Совета безопасности России Дмитрий Медведев заявил о возможных ударах по ядерным объектам в случае атак на российские АЭС.",
    },
    {
        "title": "Впервые в истории клуб с россиянином второй год подряд выиграл ЛЧ",
        "source_domain": "rbc.ru",
        "source_url": "https://www.rbc.ru/sport/30/05/2026/6a1adf979a7947a38e50b948",
        "announce_text": "ПСЖ стал первым клубом в истории Лиги чемпионов, выигравшим турнир два года подряд с российским игроком в составе.",
    },
    {
        "title": "Умер «дедушка всех французов», философ Эдгар Морен",
        "source_domain": "rbc.ru",
        "source_url": "https://www.rbc.ru/society/30/05/2026/6a1b18769a79475037ce71fa",
        "announce_text": "На 105-м году жизни скончался выдающийся французский философ и социолог Эдгар Морен.",
    },
    # ria.ru
    {
        "title": "В Армении отслужили панихиду по жертвам атаки ВСУ в Старобельске",
        "source_domain": "ria.ru",
        "source_url": "https://ria.ru/20260530/armeniya-2095768941.html",
        "announce_text": "В храмах Русской православной церкви в Армении отслужена панихида по жертвам атаки ВСУ в Старобельске.",
    },
    {
        "title": "В США запаниковали из-за состояния Зеленского после предупреждения России",
        "source_domain": "ria.ru",
        "source_url": "https://ria.ru/20260530/zelenskiy-2095768694.html",
        "announce_text": "Владимир Зеленский испугался предупреждения России о новых ударах возмездия, заявил подполковник армии США в отставке Дэниел Дэвис.",
    },
    {
        "title": "Разрушение реакторного зала ЗАЭС влечёт новый Чернобыль — Медведев",
        "source_domain": "ria.ru",
        "source_url": "https://ria.ru/20260530/medvedev-2095767744.html",
        "announce_text": "Дмитрий Медведев заявил, что катастрофическое разрушение реакторного зала атомной электростанции повлечёт последствия, сопоставимые с Чернобыльской катастрофой.",
    },
    {
        "title": "Суд обязал Трампа ответить на обвинения в сговоре по делу против налоговой",
        "source_domain": "ria.ru",
        "source_url": "https://ria.ru/20260530/sud-2095766265.html",
        "announce_text": "Суд в Соединённых Штатах обязал президента страны Дональда Трампа ответить на обвинения в «сговоре» по делу против налоговой службы.",
    },
]
# fmt: on

_BASE_DATE = datetime(2026, 5, 30, 8, 0, 0, tzinfo=UTC)


async def seed() -> None:
    async with SessionLocal() as session:
        count = (await session.execute(select(func.count()).select_from(News))).scalar_one()
        if count > 0:
            print(f"Seed skipped: {count} rows already exist.")
            return

        rows = [
            News(
                title=item["title"],
                source_url=item["source_url"],
                source_domain=item["source_domain"],
                published_at=_BASE_DATE + timedelta(minutes=i * 15),
                announce_text=item.get("announce_text"),
                enrichment_status=EnrichmentStatus.pending,
            )
            for i, item in enumerate(SEED_DATA)
        ]
        session.add_all(rows)
        await session.commit()
        print(f"Seeded {len(rows)} news rows.")


if __name__ == "__main__":
    asyncio.run(seed())
