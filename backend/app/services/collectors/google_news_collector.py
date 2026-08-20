import feedparser
import ssl
from datetime import datetime, timezone
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.schema import Ticker, RawItem

# Bypass SSL for feedparser
ssl._create_default_https_context = ssl._create_unverified_context

async def collect_google_news(session: AsyncSession, ticker_id: int = None) -> int:
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
    
    import urllib.parse
    for ticker in tickers:
        encoded_query = urllib.parse.quote(f"{ticker.symbol} stock OR share")
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        try:
            feed = await asyncio.to_thread(feedparser.parse, url)
            
            for entry in feed.entries[:15]:
                link = entry.get('link', '')
                if not link or link in existing_urls:
                    continue
                    
                existing_urls.add(link)
                title = entry.get('title', '')
                author = entry.get('source', {}).get('title', 'google_news')
                
                published = entry.get('published_parsed')
                if published:
                    dt = datetime(*published[:6]).replace(tzinfo=timezone.utc)
                else:
                    dt = datetime.now(timezone.utc)
                
                items_to_add.append(RawItem(
                    ticker_id=ticker.id,
                    platform="news",
                    source_url=link,
                    author=author,
                    text=title,
                    collected_at=dt
                ))
        except Exception as e:
            print(f"Error fetching Google News for {ticker.symbol}: {e}")

    if items_to_add:
        session.add_all(items_to_add)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Google News insert error: {e}")

    return len(items_to_add)
