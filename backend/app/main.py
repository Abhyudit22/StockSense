from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.sentiment import router as sentiment_router
from app.api.ws import router as ws_router
from app.api.analytics import router as analytics_router
from app.api.dashboard import router as dashboard_router
from app.core.config import settings
from app.workers.scheduler import start_scheduler, scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start background data collection scheduler
    start_scheduler()
    yield
    # Shutdown: stop the scheduler gracefully
    if scheduler.running:
        scheduler.shutdown(wait=False)

app = FastAPI(title="Stock Sentiment API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if "," in settings.CORS_ORIGINS else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sentiment_router)
app.include_router(ws_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
