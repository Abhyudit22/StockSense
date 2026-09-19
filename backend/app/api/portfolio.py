from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.models.schema import Portfolio, PortfolioPosition, PortfolioTransaction, Ticker
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])

class TradeRequest(BaseModel):
    symbol: str
    shares: int
    price: float
    transaction_type: str # "BUY" or "SELL"

@router.get("/")
async def get_portfolio_summary(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Ensure portfolio exists
    stmt = select(Portfolio).where(Portfolio.user_id == int(user_id))
    portfolio = (await db.execute(stmt)).scalars().first()
    
    if not portfolio:
        portfolio = Portfolio(user_id=int(user_id))
        db.add(portfolio)
        await db.commit()
        await db.refresh(portfolio)
        
    # Get positions
    pos_stmt = select(PortfolioPosition, Ticker.symbol).join(Ticker).where(PortfolioPosition.portfolio_id == portfolio.id)
    results = (await db.execute(pos_stmt)).all()
    
    positions = []
    for pos, symbol in results:
        positions.append({
            "symbol": symbol,
            "shares": pos.shares,
            "average_price": pos.average_price
        })
        
    return {
        "cash_balance": portfolio.cash_balance,
        "positions": positions
    }

@router.post("/trade")
async def execute_trade(
    trade: TradeRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if trade.shares <= 0 or trade.price <= 0:
        raise HTTPException(status_code=400, detail="Invalid trade parameters")
        
    stmt = select(Portfolio).where(Portfolio.user_id == int(user_id))
    portfolio = (await db.execute(stmt)).scalars().first()
    
    if not portfolio:
        portfolio = Portfolio(user_id=int(user_id))
        db.add(portfolio)
        await db.flush()
        
    # Get ticker
    ticker_stmt = select(Ticker).where(Ticker.symbol == trade.symbol)
    ticker = (await db.execute(ticker_stmt)).scalars().first()
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
        
    # Get position
    pos_stmt = select(PortfolioPosition).where(
        PortfolioPosition.portfolio_id == portfolio.id,
        PortfolioPosition.ticker_id == ticker.id
    )
    position = (await db.execute(pos_stmt)).scalars().first()
    
    cost = trade.shares * trade.price
    
    if trade.transaction_type.upper() == "BUY":
        if portfolio.cash_balance < cost:
            raise HTTPException(status_code=400, detail="Insufficient funds")
            
        portfolio.cash_balance -= cost
        
        if position:
            total_cost = (position.shares * position.average_price) + cost
            position.shares += trade.shares
            position.average_price = total_cost / position.shares
        else:
            position = PortfolioPosition(
                portfolio_id=portfolio.id,
                ticker_id=ticker.id,
                shares=trade.shares,
                average_price=trade.price
            )
            db.add(position)
            
    elif trade.transaction_type.upper() == "SELL":
        if not position or position.shares < trade.shares:
            raise HTTPException(status_code=400, detail="Insufficient shares")
            
        portfolio.cash_balance += cost
        position.shares -= trade.shares
        
        if position.shares == 0:
            await db.delete(position)
            
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")
        
    transaction = PortfolioTransaction(
        portfolio_id=portfolio.id,
        ticker_id=ticker.id,
        shares=trade.shares,
        price_at_execution=trade.price,
        transaction_type=trade.transaction_type.upper()
    )
    db.add(transaction)
    
    await db.commit()
    
    return {"status": "success", "message": f"{trade.transaction_type} executed"}
