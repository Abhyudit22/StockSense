import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models.schema import Base, Ticker, RawItem, SentimentScore, TickerDailySentiment

from app.core.config import settings
DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def seed_data():
    async with async_session() as session:
        from sqlalchemy.future import select

        # 1. Get or Create Tickers
        async def get_or_create(sym, n, c_n):
            result = await session.execute(select(Ticker).where(Ticker.symbol == sym))
            t = result.scalars().first()
            if not t:
                t = Ticker(symbol=sym, name=n, company_name=c_n, tracked_since=datetime.now(timezone.utc))
                session.add(t)
                await session.commit()
                await session.refresh(t)
            return t

        rel = await get_or_create("RELIANCE", "Reliance", "Reliance Industries")
        tcs = await get_or_create("TCS", "TCS", "Tata Consultancy Services")
        infy = await get_or_create("INFY", "Infosys", "Infosys Ltd")
        hdfc = await get_or_create("HDFCBANK", "HDFC Bank", "HDFC Bank Ltd")
        tata = await get_or_create("TATASTEEL", "Tata Steel", "Tata Steel Ltd")

        
        # 2. Create Raw Items & Sentiment Scores
        import random
        now = datetime.now(timezone.utc)
        items = []
        scores = []
        for ticker in [rel, tcs, infy, hdfc, tata]:
            for i in range(10):
                item = RawItem(
                    ticker_id=ticker.id,
                    platform=random.choice(["mastodon", "news", "stocktwits"]),
                    source_url=f"https://example.com/{ticker.symbol}/post{i}",
                    author=f"user{i}",
                    text=f"This is a dummy post about {ticker.symbol} that has some sentiment. Buy it!",
                    collected_at=now - timedelta(minutes=random.randint(1, 60))
                )
                items.append(item)
                
        session.add_all(items)
        await session.commit()
        
        for item in items:
            score = SentimentScore(
                raw_item_id=item.id,
                score=random.uniform(-1.0, 1.0),
                model_version="finbert-v1",
                computed_at=item.collected_at
            )
            scores.append(score)
            
        session.add_all(scores)
        
        # 3. Create Daily Sentiment
        for ticker in [rel, tcs, infy, hdfc, tata]:
            for i in range(30):
                daily = TickerDailySentiment(
                    ticker_id=ticker.id,
                    date=(now - timedelta(days=i)).replace(tzinfo=None),
                    aggregate_score=random.uniform(-0.8, 0.9),
                    volume=random.randint(10, 500),
                    confidence=random.uniform(0.5, 0.9)
                )
                session.add(daily)
                
        await session.commit()
        print("Successfully seeded mock data!")

if __name__ == "__main__":
    asyncio.run(seed_data())
