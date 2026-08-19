from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class Ticker(Base):
    __tablename__ = "tickers"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

class RawItem(Base):
    __tablename__ = "raw_items"
    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    platform = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    author = Column(String)
    text = Column(Text, nullable=False)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())

class SentimentScore(Base):
    __tablename__ = "sentiment_scores"
    id = Column(Integer, primary_key=True, index=True)
    raw_item_id = Column(Integer, ForeignKey("raw_items.id"), nullable=False)
    score = Column(Float, nullable=False)
    model_version = Column(String, nullable=False)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

class TickerDailySentiment(Base):
    __tablename__ = "ticker_daily_sentiment"
    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    aggregate_score = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    confidence = Column(Float)

class IPOFiling(Base):
    __tablename__ = "ipo_filings"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    ticker = Column(String, nullable=False)
    filing_date = Column(DateTime, nullable=False)
    s1_url = Column(String, nullable=False)

class IPOReport(Base):
    __tablename__ = "ipo_reports"
    id = Column(Integer, primary_key=True, index=True)
    ipo_filing_id = Column(Integer, ForeignKey("ipo_filings.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    report_json = Column(JSON, nullable=False)
    sources = Column(JSON)

class AgentEvent(Base):
    __tablename__ = "agent_events"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=True)
    step_name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
