import httpx
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.schema import Ticker, RawItem

async def collect_news(session: AsyncSession, ticker_id: int = None) -> int:
    stmt = select(Ticker)
    if ticker_id:
        stmt = stmt.where(Ticker.id == ticker_id)
    result = await session.execute(stmt)
    tickers = result.scalars().all()
    if not tickers:
        return 0

    # Fetch existing URLs for deduplication
    existing_stmt = select(RawItem.source_url).where(
        RawItem.ticker_id.in_([t.id for t in tickers])
    )
    existing_urls = set((await session.execute(existing_stmt)).scalars().all())

    items_to_add = []

    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        for ticker in tickers:
            url = (
                f"https://api.gdeltproject.org/api/v2/doc/doc"
                f"?query={ticker.symbol} sourcelang:eng&mode=artlist&format=json"
            )
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    articles = data.get("articles", [])[:15]
                    for art in articles:
                        article_url = art.get("url", "")
                        if not article_url or article_url in existing_urls:
                            continue
                        existing_urls.add(article_url)

                        # GDELT date format: 20260815T120000Z
                        try:
                            date_str = art.get('seendate', '')
                            dt = datetime.strptime(date_str, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
                        except Exception:
                            dt = datetime.now(timezone.utc)

                        items_to_add.append(RawItem(
                            ticker_id=ticker.id,
                            platform="news",
                            source_url=article_url,
                            author=art.get("domain", "news_outlet"),
                            text=f"{art.get('title', '')} - {art.get('domain', '')}",
                            collected_at=dt
                        ))
            except Exception as e:
                print(f"Error fetching GDELT news for {ticker.symbol}: {e}")

    if items_to_add:
        session.add_all(items_to_add)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"News insert error: {e}")

    return len(items_to_add)
