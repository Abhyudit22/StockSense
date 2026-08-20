from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func
from datetime import datetime, timezone, timedelta

from app.db.session import async_session
from app.models.schema import Ticker, RawItem, SentimentScore, TickerDailySentiment
from app.schemas.sentiment import SentimentResponse, TrendDataPoint, SourcesPaginatedResponse, SourceItemResponse
from app.services.sentiment.aggregator import get_aggregate_sentiment
from app.workers.scheduler import run_collectors

router = APIRouter(prefix="/api/tickers", tags=["Sentiment"])

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/{symbol}/sentiment", response_model=SentimentResponse)
async def get_ticker_sentiment(
    symbol: str, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    symbol = symbol.upper()
    stmt = select(Ticker).where(Ticker.symbol == symbol)
    ticker = (await db.execute(stmt)).scalars().first()
    
    if not ticker:
        # Validate symbol with yfinance before registering
        import yfinance as yf
        import asyncio
        
        # We append .NS for Indian National Stock Exchange
        sym_yf = symbol if symbol.endswith('.NS') or symbol.endswith('.BO') else f"{symbol}.NS"
        data = yf.download(sym_yf, period="1d", interval="1d", progress=False)
        if data.empty:
            # Fallback to no .NS if it fails
            data = yf.download(symbol, period="1d", interval="1d", progress=False)
            
        if data.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"Stock '{symbol}' not found or is delisted. Please check the stock's name and correct it."
            )
            
        # Auto-register new ticker
        ticker = Ticker(
            symbol=symbol,
            name=f"{symbol} Corp",
            company_name=f"{symbol} Corp",
            tracked_since=datetime.now(timezone.utc)
        )
        db.add(ticker)
        await db.commit()
        await db.refresh(ticker)
        
        # Trigger background collection instantly for this ticker
        background_tasks.add_task(run_collectors, ticker.id)
        
    now = datetime.now(timezone.utc)
    current = await get_aggregate_sentiment(db, ticker.id, now)
    
    import yfinance as yf
    import asyncio
    
    def fetch_price_history(sym):
        try:
            # We append .NS for Indian National Stock Exchange
            sym_yf = sym if sym.endswith('.NS') or sym.endswith('.BO') else f"{sym}.NS"
            data = yf.download(sym_yf, period="1mo", interval="1d", progress=False)
            if data.empty:
                # Fallback to no .NS if it fails
                data = yf.download(sym, period="1mo", interval="1d", progress=False)
            
            history = []
            if not data.empty:
                # yfinance returns multi-index columns even for a single symbol in recent versions
                for date, row in data.iterrows():
                    try:
                        close_val = row['Close'].iloc[0] if isinstance(row['Close'], type(row)) else row['Close']
                        vol_val = row['Volume'].iloc[0] if 'Volume' in row and isinstance(row['Volume'], type(row)) else row.get('Volume', 0)
                        history.append(TrendDataPoint(
                            date=date.strftime("%Y-%m-%d"),
                            score=float(close_val),
                            volume=int(vol_val)
                        ))
                    except Exception as e:
                        pass
            return history
        except Exception:
            return []
            
    trend_data = await asyncio.to_thread(fetch_price_history, symbol)
    
    score = current.get("aggregate_score", 0.0)
    vol = current.get("volume", 0)
    
    if vol < 3:
        ai_analysis = f"Insufficient data points ({vol} mentions) to form a reliable analysis. Background agents are actively scanning for more mentions."
    else:
        # Fetch the most recent items to extract keywords
        stmt_recent = (
            select(RawItem.text)
            .where(RawItem.ticker_id == ticker.id)
            .order_by(desc(RawItem.collected_at))
            .limit(20)
        )
        recent_texts = (await db.execute(stmt_recent)).scalars().all()
        
        if score > 0.2:
            base = "Strong positive momentum detected."
        elif score < -0.2:
            base = "Significant bearish sentiment observed."
        else:
            base = "Overall sentiment is currently neutral."

        # Use OpenRouter for real AI analysis if API key is provided
        from app.core.config import settings
        if settings.OPENROUTER_API_KEY:
            import httpx
            
            # Combine the top recent texts to give context to the LLM
            context_texts = [text for text in recent_texts if len(text.strip()) > 10][:10]
            context_str = "\n- ".join(context_texts)
            
            prompt = f"You are a financial sentiment analyst. Given the following recent mentions for {symbol} (sentiment score: {score:.2f} out of 1.0, where >0 is positive), write a concise 1-2 sentence summary of the main topics or narratives driving this sentiment. Do not give financial advice. Keep it under 250 characters. Mentions:\n- {context_str}"
            
            try:
                # Use a fast free model like mistralai/mistral-7b-instruct:free or google/gemini-2.5-flash:free
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                            "HTTP-Referer": "http://localhost:8000",
                            "X-Title": "Market Pulse"
                        },
                        json={
                            "model": "google/gemma-4-31b-it:free",
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 100,
                            "temperature": 0.3
                        },
                        timeout=5.0
                    )
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        ai_analysis = data["choices"][0]["message"]["content"].strip()
                    else:
                        ai_analysis = f"{base} (Note: OpenRouter API error {resp.status_code})"
            except Exception as e:
                ai_analysis = f"{base} (Note: OpenRouter analysis failed: {e})"
        else:
            # Fallback naive keyword extraction
            # Extremely naive keyword extraction (ignoring common stop words)
            stop_words = {"the", "is", "at", "which", "on", "and", "a", "to", "of", "in", "for", "with", "as", "it", "this", "that", "by", "from", "are", "be", "was", "has", "have", "not", "but", "or", "an", "they", "will", "would", "can", "about", "what", "their", "our", "we", "you", "he", "she", "it", "his", "hers", "its", "up", "out", "if", "so", "do", "all", "no", "one", "more", "stock", "shares", "company", "market", "inc", "corp", "ltd", "new", "just", "like", "how", "when", "who", "why", "get", "now", "today"}
            
            word_counts = {}
            for text in recent_texts:
                import re
                words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
                for w in words:
                    if w not in stop_words and w != symbol.lower():
                        word_counts[w] = word_counts.get(w, 0) + 1
                        
            # Get top 3 keywords
            top_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            keyword_str = ", ".join([f"'{k}'" for k, v in top_keywords])
            if keyword_str:
                ai_analysis = f"{base} Across {vol} recent mentions, discussion is heavily concentrated around topics like {keyword_str}. Technical and retail channels are aligning with this narrative."
            else:
                ai_analysis = f"{base} Based on {vol} recent data points, the market is digesting general news without a single dominant keyword."
    
    return SentimentResponse(
        symbol=symbol,
        current_score=score,
        volume=current.get("volume", 0),
        confidence=current.get("confidence", 0.0),
        trend_30_days=trend_data,
        ai_analysis=ai_analysis
    )

@router.get("/{symbol}/sources", response_model=SourcesPaginatedResponse)
async def get_ticker_sources(
    symbol: str, 
    page: int = Query(1, ge=1), 
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    symbol = symbol.upper()
    stmt = select(Ticker).where(Ticker.symbol == symbol)
    ticker = (await db.execute(stmt)).scalars().first()
    
    if not ticker:
        # If they somehow hit sources before sentiment, return empty immediately
        return SourcesPaginatedResponse(
            symbol=symbol,
            items=[],
            total=0,
            page=page,
            size=size
        )
        
    offset = (page - 1) * size
    
    stmt_count = (
        select(func.count(RawItem.id))
        .where(RawItem.ticker_id == ticker.id)
        .join(SentimentScore, RawItem.id == SentimentScore.raw_item_id)
    )
    total = (await db.execute(stmt_count)).scalar()
    
    stmt_items = (
        select(RawItem, SentimentScore)
        .join(SentimentScore, RawItem.id == SentimentScore.raw_item_id)
        .where(RawItem.ticker_id == ticker.id)
        .order_by(desc(RawItem.collected_at))
        .offset(offset)
        .limit(size)
    )
    results = (await db.execute(stmt_items)).all()
    
    items = []
    for raw, score in results:
        items.append(SourceItemResponse(
            id=raw.id,
            platform=raw.platform,
            source_url=raw.source_url,
            author=raw.author,
            text=raw.text,
            score=score.score,
            collected_at=raw.collected_at
        ))
        
    return SourcesPaginatedResponse(
        symbol=symbol,
        items=items,
        total=total or 0,
        page=page,
        size=size
    )
