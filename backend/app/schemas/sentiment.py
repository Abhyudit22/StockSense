from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class TrendDataPoint(BaseModel):
    date: str
    score: float
    volume: int

class SentimentResponse(BaseModel):
    symbol: str
    current_score: float
    volume: int
    confidence: float
    trend_30_days: List[TrendDataPoint]
    ai_analysis: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "NVDA",
                "current_score": 0.45,
                "volume": 120,
                "confidence": 0.95,
                "trend_30_days": [
                    {"date": "2026-08-15", "score": 0.3, "volume": 50},
                    {"date": "2026-08-16", "score": 0.45, "volume": 120}
                ]
            }
        }
    )

class SourceItemResponse(BaseModel):
    id: int
    platform: str
    source_url: str
    author: Optional[str] = None
    text: str
    score: float
    collected_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SourcesPaginatedResponse(BaseModel):
    symbol: str
    items: List[SourceItemResponse]
    total: int
    page: int
    size: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "NVDA",
                "items": [
                    {
                        "id": 1,
                        "platform": "stocktwits",
                        "source_url": "https://stocktwits.com/symbol/NVDA",
                        "author": "stock_trader",
                        "text": "NVDA is hitting new highs!",
                        "score": 0.8,
                        "collected_at": "2026-08-19T20:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 20
            }
        }
    )
