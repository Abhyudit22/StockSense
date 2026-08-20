import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc
from app.models.schema import Ticker, TickerDailySentiment

async def calculate_sentiment_correlation(session: AsyncSession, ticker_symbol: str, days: int = 30) -> dict:
    # 1. Fetch Ticker
    stmt = select(Ticker).where(Ticker.symbol == ticker_symbol.upper())
    ticker = (await session.execute(stmt)).scalars().first()
    if not ticker:
        raise ValueError(f"Ticker {ticker_symbol} not found")

    # 2. Fetch Historical Sentiment
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    stmt_sent = (
        select(TickerDailySentiment)
        .where(TickerDailySentiment.ticker_id == ticker.id)
        .where(TickerDailySentiment.date >= start_date)
        .order_by(asc(TickerDailySentiment.date))
    )
    sentiment_records = (await session.execute(stmt_sent)).scalars().all()
    
    if not sentiment_records:
        return {"correlation": None, "message": "No sentiment data available for correlation"}

    # Build Sentiment DataFrame
    sent_df = pd.DataFrame([{
        'date': sr.date.strftime('%Y-%m-%d'),
        'sentiment': sr.aggregate_score
    } for sr in sentiment_records])
    sent_df['date'] = pd.to_datetime(sent_df['date'])
    sent_df.set_index('date', inplace=True)

    # 3. Fetch Historical Price Data
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    yf_ticker = yf.Ticker(ticker.symbol)
    
    try:
        price_df = yf_ticker.history(start=start_str, end=end_str)
    except Exception as e:
        return {"correlation": None, "message": f"Failed to fetch price data from yfinance: {e}"}
        
    if price_df.empty:
        return {"correlation": None, "message": "No price data available"}

    # Calculate daily returns
    price_df['return'] = price_df['Close'].pct_change()
    
    # Make price_df index timezone naive to match sentiment format
    if price_df.index.tz is not None:
        price_df.index = price_df.index.tz_localize(None)

    # 4. Merge DataFrames on Date
    merged = pd.merge(sent_df, price_df, left_index=True, right_index=True, how='inner')
    
    if merged.empty or len(merged) < 3:
        return {"correlation": None, "message": "Insufficient overlapping data points"}

    # 5. Calculate Pearson Correlation
    merged['forward_return'] = merged['return'].shift(-1)
    
    corr_price = merged['sentiment'].corr(merged['Close'])
    corr_return = merged['sentiment'].corr(merged['forward_return'])

    return {
        "correlation_price": float(corr_price) if pd.notna(corr_price) else None,
        "correlation_forward_return": float(corr_return) if pd.notna(corr_return) else None,
        "data_points": len(merged),
        "message": "Correlation calculated successfully"
    }
