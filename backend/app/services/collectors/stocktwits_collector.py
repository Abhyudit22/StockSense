import httpx
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from bs4 import BeautifulSoup
from app.models.schema import Ticker, RawItem

async def collect_stocktwits(session: AsyncSession, ticker_id: int = None) -> int:
    """
    Re-purposed to collect from Mastodon (Free/Open Social Media)
    instead of StockTwits, which now blocks free access.
    """
    stmt = select(Ticker)
    if ticker_id:
        stmt = stmt.where(Ticker.id == ticker_id)
    result = await session.execute(stmt)
    tickers = result.scalars().all()
    if not tickers:
        return 0

    existing_stmt = select(RawItem.source_url).where(
        RawItem.ticker_id.in_([t.id for t in tickers])
    )
    existing_urls = set((await session.execute(existing_stmt)).scalars().all())

    items_to_add = []

    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        for ticker in tickers:
            # We search for the ticker symbol as a hashtag, e.g. #AAPL
            url = f"https://mastodon.social/api/v1/timelines/tag/{ticker.symbol}"
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    posts = resp.json()
                    for post in posts[:15]:
                        source_url = post.get('url')
                        if not source_url or source_url in existing_urls:
                            continue
                        existing_urls.add(source_url)

                        created_at_str = post.get('created_at')
                        try:
                            # 2026-08-19T20:45:00.000Z
                            created_at = datetime.strptime(
                                created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                            ).replace(tzinfo=timezone.utc)
                        except Exception:
                            created_at = datetime.now(timezone.utc)

                        # Clean HTML tags from content
                        html_content = post.get('content', '')
                        text = BeautifulSoup(html_content, "html.parser").get_text()

                        author = post.get('account', {}).get('username', 'mastodon_user')

                        items_to_add.append(RawItem(
                            ticker_id=ticker.id,
                            platform="mastodon",
                            source_url=source_url,
                            author=author,
                            text=text[:2000],
                            collected_at=created_at
                        ))
            except Exception as e:
                print(f"Error fetching Mastodon for {ticker.symbol}: {e}")

    if items_to_add:
        session.add_all(items_to_add)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Mastodon insert error: {e}")

    return len(items_to_add)
