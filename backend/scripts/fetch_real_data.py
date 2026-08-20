import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import async_session
from app.models.schema import RawItem, SentimentScore, TickerDailySentiment
from sqlalchemy import delete
from app.workers.scheduler import run_collectors

async def clear_dummy_and_collect():
    async with async_session() as session:
        print("Clearing dummy data...")
        await session.execute(delete(SentimentScore))
        await session.execute(delete(TickerDailySentiment))
        await session.execute(delete(RawItem))
        await session.commit()
        
    print("Starting real data collection from Google News, StockTwits, etc...")
    await run_collectors()
    print("Finished collecting real data! Refresh your dashboard.")

if __name__ == "__main__":
    asyncio.run(clear_dummy_and_collect())
