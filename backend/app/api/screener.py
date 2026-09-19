from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from app.db.session import get_db
from app.models.schema import Ticker, TickerDailySentiment, RawItem
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/api/screener", tags=["Screener"])

class ScreenerResult(BaseModel):
    symbol: str
    name: str
    current_score: float
    volume: int

@router.get("/search", response_model=List[ScreenerResult])
async def search_screener(
    min_score: Optional[float] = Query(None, description="Minimum sentiment score (-1 to 1)"),
    max_score: Optional[float] = Query(None, description="Maximum sentiment score (-1 to 1)"),
    min_volume: Optional[int] = Query(None, description="Minimum mention volume"),
    query: Optional[str] = Query(None, description="Search by symbol or name"),
    db: AsyncSession = Depends(get_db)
):
    # Get latest daily sentiment for each ticker
    now = datetime.now(timezone.utc)
    
    # Simple subquery for latest sentiment per ticker
    stmt = select(Ticker.symbol, Ticker.name, TickerDailySentiment.aggregate_score, TickerDailySentiment.volume)\
        .outerjoin(TickerDailySentiment, Ticker.id == TickerDailySentiment.ticker_id)
        
    if query:
        stmt = stmt.where(or_(
            Ticker.symbol.ilike(f"%{query}%"),
            Ticker.name.ilike(f"%{query}%")
        ))
        
    results = (await db.execute(stmt)).all()
    
    # Process results (we do it in python to handle fallbacks easily)
    final_results = []
    
    for row in results:
        symbol, name, score, vol = row
        score = score if score is not None else 0.0
        vol = vol if vol is not None else 0
        
        # Apply filters
        if min_score is not None and score < min_score:
            continue
        if max_score is not None and score > max_score:
            continue
        if min_volume is not None and vol < min_volume:
            continue
            
        final_results.append(ScreenerResult(
            symbol=symbol,
            name=name or symbol,
            current_score=score,
            volume=vol
        ))
        
    # Sort by volume descending as default
    final_results.sort(key=lambda x: x.volume, reverse=True)
    return final_results
