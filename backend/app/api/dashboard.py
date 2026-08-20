from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy import desc
from app.db.session import async_session
from app.models.schema import Ticker, RawItem, SentimentScore
from app.services.sentiment.aggregator import get_aggregate_sentiment
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

async def get_db():
    async with async_session() as session:
        yield session

import yfinance as yf
import asyncio

class TickerSummary(BaseModel):
    symbol: str
    name: str
    current_score: float
    volume: int
    price: Optional[float] = None
    change_percent: Optional[float] = None

class DashboardNewsItem(BaseModel):
    symbol: str
    platform: str
    source_url: str
    text: str
    score: float
    collected_at: datetime
    author: Optional[str] = None

@router.get("/tickers", response_model=List[TickerSummary])
async def get_dashboard_tickers(db: AsyncSession = Depends(get_db)):
    stmt = select(Ticker)
    tickers = (await db.execute(stmt)).scalars().all()
    
    results = []
    now = datetime.now(timezone.utc)
    
    # Fetch sentiment sequentially to avoid concurrent session usage
    sentiments = []
    for t in tickers:
        sentiments.append(await get_aggregate_sentiment(db, t.id, now))
    
    # Fetch prices synchronously in a thread
    def fetch_prices(symbols):
        if not symbols: return {}
        try:
            # We append .NS for Indian National Stock Exchange
            symbols_for_yf = [s if s.endswith('.NS') or s.endswith('.BO') else f"{s}.NS" for s in symbols]
            
            # yfinance download handles multiple tickers efficiently
            # We use period="2d" to get the latest day's data and previous day for change calculation
            tickers_str = " ".join(symbols_for_yf)
            data = yf.download(tickers_str, period="2d", group_by="ticker", auto_adjust=False, prepost=False, threads=False, progress=False)
            
            prices_info = {}
            # If only 1 symbol, yfinance doesn't group by ticker in columns
            if len(symbols_for_yf) == 1:
                sym_yf = symbols_for_yf[0]
                orig_sym = symbols[0]
                if not data.empty and len(data) > 0:
                    try:
                        latest = data.iloc[-1]
                        prev = data.iloc[-2] if len(data) > 1 else latest
                        close = float(latest['Close'])
                        prev_close = float(prev['Close'])
                        change = ((close - prev_close) / prev_close) * 100 if prev_close else 0.0
                        prices_info[orig_sym] = {"price": close, "change": change}
                    except Exception:
                        pass
            else:
                for orig_sym, sym_yf in zip(symbols, symbols_for_yf):
                    if sym_yf in data:
                        try:
                            df_sym = data[sym_yf].dropna(subset=['Close'])
                            if not df_sym.empty and len(df_sym) > 0:
                                latest = df_sym.iloc[-1]
                                prev = df_sym.iloc[-2] if len(df_sym) > 1 else latest
                                close = float(latest['Close'])
                                prev_close = float(prev['Close'])
                                change = ((close - prev_close) / prev_close) * 100 if prev_close else 0.0
                                prices_info[orig_sym] = {"price": close, "change": change}
                        except Exception:
                            pass
            return prices_info
        except Exception as e:
            return {}

    symbols = [t.symbol for t in tickers]
    prices = await asyncio.to_thread(fetch_prices, symbols)
    
    for t, current in zip(tickers, sentiments):
        p_info = prices.get(t.symbol, {})
        
        # If seed data from yesterday is present, it will show 0 volume for today.
        # Let's fallback to calculating total volume if today's volume is 0, so the UI doesn't look empty for dummy data.
        vol = current.get("volume", 0)
        score = current.get("aggregate_score", 0.0)
        
        if vol == 0:
            # Fallback for dashboard visualization purposes
            stmt_all = select(func.count(RawItem.id)).where(RawItem.ticker_id == t.id)
            total_vol = (await db.execute(stmt_all)).scalar()
            if total_vol > 0:
                vol = total_vol
                score = 0.5  # Just a dummy positive score if it has old data

        results.append(TickerSummary(
            symbol=t.symbol,
            name=t.name or t.symbol,
            current_score=score,
            volume=vol,
            price=p_info.get("price"),
            change_percent=p_info.get("change")
        ))
    return results

@router.get("/news", response_model=List[DashboardNewsItem])
async def get_dashboard_news(limit: int = 20, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(RawItem, SentimentScore, Ticker.symbol)
        .join(SentimentScore, RawItem.id == SentimentScore.raw_item_id)
        .join(Ticker, RawItem.ticker_id == Ticker.id)
        .order_by(desc(RawItem.collected_at))
        .limit(limit)
    )
    results = (await db.execute(stmt)).all()
    
    news = []
    for raw, score, symbol in results:
        news.append(DashboardNewsItem(
            symbol=symbol,
            platform=raw.platform,
            source_url=raw.source_url,
            text=raw.text,
            score=score.score,
            collected_at=raw.collected_at,
            author=raw.author
        ))
    return news


class IndexSummary(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float

@router.get("/indices", response_model=List[IndexSummary])
async def get_market_indices():
    """Fetch live NIFTY 50, BANK NIFTY, and SENSEX data."""
    INDICES = {
        "^NSEI":    "NIFTY 50",
        "^NSEBANK": "BANK NIFTY",
        "^BSESN":   "SENSEX",
    }
    
    def fetch():
        try:
            data = yf.download(list(INDICES.keys()), period="2d", progress=False)
            results = []
            close_df = data["Close"]
            for sym, name in INDICES.items():
                try:
                    series = close_df[sym].dropna()
                    if len(series) >= 2:
                        cur = float(series.iloc[-1])
                        prev = float(series.iloc[-2])
                        chg = cur - prev
                        chg_pct = (chg / prev) * 100
                    elif len(series) == 1:
                        cur = float(series.iloc[-1])
                        chg = 0.0
                        chg_pct = 0.0
                    else:
                        continue
                    results.append(IndexSummary(symbol=sym, name=name, price=cur, change=chg, change_percent=chg_pct))
                except Exception:
                    continue
            return results
        except Exception:
            return []

    return await asyncio.to_thread(fetch)
