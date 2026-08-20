import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from app.services.sentiment.aggregator import get_aggregate_sentiment
from app.services.sentiment.finbert_model import SentimentEngine

def test_sentiment_engine():
    engine = SentimentEngine()
    # Use explicitly financial terms for FinBERT
    texts = [
        "The company reported a massive earnings beat, raising revenue guidance.", 
        "Revenue plummeted by 50%, missing all analyst expectations significantly."
    ]
    results = engine.score_batch(texts)
    assert len(results) == 2
    assert results[0]['score'] > 0  # Positive
    assert results[1]['score'] < 0  # Negative

@pytest.mark.asyncio
@patch("app.services.sentiment.aggregator.redis_client")
async def test_get_aggregate_sentiment(mock_redis):
    mock_redis.get.return_value = None
    
    mock_session = AsyncMock()
    # Explicitly mock synchronous SQLAlchemy session methods
    mock_session.add = MagicMock()
    mock_session.add_all = MagicMock()
    
    mock_unscored = MagicMock()
    mock_unscored.scalars.return_value.all.return_value = []
    
    mock_agg = MagicMock()
    now = datetime.now(timezone.utc)
    mock_agg.all.return_value = [
        (now, 0.8, 1),
        (now, 0.6, 2)
    ]
    
    mock_daily = MagicMock()
    mock_daily.scalars.return_value.first.return_value = None
    
    mock_session.execute.side_effect = [mock_unscored, mock_agg, mock_daily]
    
    result = await get_aggregate_sentiment(mock_session, ticker_id=1, date=now)
    
    assert "aggregate_score" in result
    assert result["aggregate_score"] == 0.7
    assert result["volume"] == 2
    
    mock_redis.setex.assert_called_once()
