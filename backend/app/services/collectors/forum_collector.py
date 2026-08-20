import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import yfinance as yf
from app.models.schema import Ticker, RawItem

async def collect_forum_mentions(session: AsyncSession, ticker_id: int = None) -> int:
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

    for ticker in tickers:
        try:
            # yfinance network calls can be blocking, but we use to_thread to keep it async
            def fetch_news():
                return yf.Ticker(ticker.symbol).news
                
            news = await asyncio.to_thread(fetch_news)
            
            for item in news:
                link = item.get("link", "")
                if not link or link in existing_urls:
                    continue
                existing_urls.add(link)
                
                title = item.get("title", "")
                publisher = item.get("publisher", "yahoo_finance")
                
                # yfinance provides providerPublishTime in unix timestamp
                pub_time = item.get("providerPublishTime")
                if pub_time:
                    dt = datetime.fromtimestamp(pub_time, tz=timezone.utc)
                else:
                    dt = datetime.now(timezone.utc)
                
                items_to_add.append(RawItem(
                    ticker_id=ticker.id,
                    platform="yahoo_finance",
                    source_url=link,
                    author=publisher,
                    text=title,
                    collected_at=dt
                ))
        except Exception as e:
            print(f"Error fetching yfinance news for {ticker.symbol}: {e}")

    if items_to_add:
        session.add_all(items_to_add)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Yahoo Finance insert error: {e}")

    return len(items_to_add)
