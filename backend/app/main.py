from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter
from app.api.sentiment import router as sentiment_router
from app.api.ws import router as ws_router
from app.api.analytics import router as analytics_router
from app.api.dashboard import router as dashboard_router
from app.api.auth import router as auth_router
from app.api.portfolio import router as portfolio_router
from app.api.screener import router as screener_router
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

app = FastAPI(title="StockSense API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if "," in settings.CORS_ORIGINS else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(sentiment_router)
app.include_router(ws_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)
app.include_router(portfolio_router)
app.include_router(screener_router)

@app.get("/health")
@limiter.limit("5/minute")
async def health(request: Request):
    return {"status": "ok"}
