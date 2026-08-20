import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schema import AgentEvent
from app.core.config import settings
import redis.asyncio as redis

from typing import Optional

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def publish_event(session: AsyncSession, job_id: str, ticker_id: Optional[int], step_name: str, message: str):
    try:
        # Write to DB
        event = AgentEvent(
            job_id=job_id,
            ticker_id=ticker_id,
            step_name=step_name,
            message=message,
            timestamp=datetime.now(timezone.utc)
        )

        session.add(event)
        await session.commit()
        
        # Publish to Redis
        payload = {
            "id": event.id,
            "job_id": job_id,
            "ticker_id": ticker_id,
            "step_name": step_name,
            "message": message,
            "timestamp": event.timestamp.isoformat()
        }
        await redis_client.publish("agent_events", json.dumps(payload))
    except Exception as e:
        print(f"Error publishing event: {e}")
