import json
import logging
from datetime import datetime, timezone, timedelta
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import cast, Date

from app.core.config import settings
from app.models.schema import RawItem, SentimentScore, TickerDailySentiment
from app.services.sentiment.finbert_model import SentimentEngine

from app.core.events import publish_event
import uuid

logger = logging.getLogger(__name__)

sentiment_engine = None
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_sentiment_engine():
    global sentiment_engine
    if sentiment_engine is None:
        sentiment_engine = SentimentEngine()
    return sentiment_engine

async def get_aggregate_sentiment(session: AsyncSession, ticker_id: int, date: datetime = None) -> dict:
    """
    Calculates and returns the aggregated sentiment for a given ticker and date.
    Uses a volume- and recency-weighted average.
    """
    job_id = str(uuid.uuid4())[:8]
    
    if date is None:
        date = datetime.now(timezone.utc)
        
    cache_key = f"sentiment:{ticker_id}:{date.strftime('%Y-%m-%d')}"
    
    # 1. Try Cache
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Score un-scored items
    stmt = (
        select(RawItem)
        .outerjoin(SentimentScore, RawItem.id == SentimentScore.raw_item_id)
        .where(RawItem.ticker_id == ticker_id)
        .where(SentimentScore.id == None)
    )
    unscored_items = (await session.execute(stmt)).scalars().all()
    
    if unscored_items:
        await publish_event(session, job_id, ticker_id, "Scoring", f"Scoring {len(unscored_items)} items with FinBERT")
        engine = get_sentiment_engine()
        texts = [item.text for item in unscored_items]
        
        # Run CPU-heavy FinBERT inference in a thread pool to avoid blocking the event loop
        import asyncio
        scores = await asyncio.to_thread(engine.score_batch, texts)
        
        new_scores = []
        for item, s in zip(unscored_items, scores):
            new_scores.append(SentimentScore(
                raw_item_id=item.id,
                score=s['score'],
                model_version=s['model_version']
            ))
        session.add_all(new_scores)
        await session.commit()
        await publish_event(session, job_id, ticker_id, "Scored", f"Successfully saved {len(new_scores)} scores.")

    # 3. Compute 7-Day Rolling Aggregate (more robust against low daily volume)
    start_of_window = date - timedelta(days=7)
    end_of_window = date + timedelta(days=1)

    # TickerDailySentiment.date is TIMESTAMP WITHOUT TIMEZONE — strip tz for comparison
    # We still record the date as start_of_day (for today)
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    start_naive = start_of_day.replace(tzinfo=None)

    stmt_agg = (
        select(RawItem.collected_at, SentimentScore.score, SentimentScore.id)
        .join(SentimentScore, RawItem.id == SentimentScore.raw_item_id)
        .where(RawItem.ticker_id == ticker_id)
        .where(RawItem.collected_at >= start_of_window)
        .where(RawItem.collected_at < end_of_window)
    )
    results = (await session.execute(stmt_agg)).all()
    
    volume = len(results)
    if volume == 0:
        result_dict = {"aggregate_score": 0.0, "volume": 0, "confidence": 0.0}
        # Do not cache zero-volume results so background collection can be polled
        return result_dict

    # Recency-weighted average
    total_weight = 0.0
    weighted_score_sum = 0.0
    
    for collected_at, score, _ in results:
        hours_old = (date - collected_at).total_seconds() / 3600.0
        weight = 0.5 ** (hours_old / 12.0)
        
        weighted_score_sum += score * weight
        total_weight += weight
        
    aggregate_score = weighted_score_sum / total_weight if total_weight > 0 else 0.0
    confidence = min(volume / 100.0, 1.0)
    
    # 4. Save to DB
    stmt_daily = select(TickerDailySentiment).where(
        TickerDailySentiment.ticker_id == ticker_id,
        cast(TickerDailySentiment.date, Date) == start_of_day.date()
    )
    daily_record = (await session.execute(stmt_daily)).scalars().first()
    
    if daily_record:
        daily_record.aggregate_score = aggregate_score
        daily_record.volume = volume
        daily_record.confidence = confidence
    else:
        daily_record = TickerDailySentiment(
            ticker_id=ticker_id,
            date=start_naive,
            aggregate_score=aggregate_score,
            volume=volume,
            confidence=confidence
        )
        session.add(daily_record)
        
    await session.commit()
    await publish_event(session, job_id, ticker_id, "Aggregation", f"Updated aggregate score: {aggregate_score:.2f} (Vol: {volume})")
    
    result_dict = {
        "aggregate_score": aggregate_score,
        "volume": volume,
        "confidence": confidence
    }
    
    await redis_client.setex(cache_key, 300, json.dumps(result_dict))
    
    return result_dict
