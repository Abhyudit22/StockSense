from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.services.analytics.backtester import calculate_sentiment_correlation

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/{ticker}/correlation")
async def get_correlation(ticker: str, days: int = 30, db: AsyncSession = Depends(get_db)):
    try:
        result = await calculate_sentiment_correlation(db, ticker, days)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
