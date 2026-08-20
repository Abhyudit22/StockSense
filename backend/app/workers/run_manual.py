import asyncio
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import async_session
from app.services.collectors.google_news_collector import collect_google_news
from app.services.collectors.news_collector import collect_news
from app.services.collectors.stocktwits_collector import collect_stocktwits
from app.services.collectors.forum_collector import collect_forum_mentions

logging.basicConfig(level=logging.INFO)

async def main():
    print("Running manual collection across all sources...")
    try:
        async with async_session() as session:
            g_news = await collect_google_news(session)
            n = await collect_news(session)
            s = await collect_stocktwits(session)
            f = await collect_forum_mentions(session)
            print(f"Collection complete! Added items -> GoogleNews: {g_news} | News: {n} | StockTwits: {s} | Forum: {f}")
    except Exception as e:
        print(f"Error during collection: {e}")

if __name__ == "__main__":
    asyncio.run(main())
