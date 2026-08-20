import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import async_session
from app.services.collectors.google_news_collector import collect_google_news
from app.services.collectors.news_collector import collect_news
from app.services.collectors.stocktwits_collector import collect_stocktwits
from app.services.collectors.forum_collector import collect_forum_mentions

scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)

async def _run_collector(collector_func, ticker_id):
    async with async_session() as session:
        return await collector_func(session, ticker_id)

async def run_collectors(ticker_id: int = None):
    logger.info(f"Running collectors for ticker_id={ticker_id}..." if ticker_id else "Running all data collectors...")
    try:
        results = await asyncio.gather(
            _run_collector(collect_google_news, ticker_id),
            _run_collector(collect_news, ticker_id),
            _run_collector(collect_stocktwits, ticker_id),
            _run_collector(collect_forum_mentions, ticker_id),
            return_exceptions=True
        )
        
        counts = []
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Collector failed: {r}")
                counts.append(0)
            else:
                counts.append(r)
                
        g_count, n_count, s_count, f_count = counts
        total = sum(counts)
        logger.info(f"Collection complete. Total new items: {total}")
        logger.info(f"Breakdown: GoogleNews={g_count}, News={n_count}, StockTwits={s_count}, Forums={f_count}")
            
    except Exception as e:
        logger.error(f"Failed to run collectors: {e}")

def start_scheduler():
    # Schedule all collectors to run every 15 minutes
    scheduler.add_job(run_collectors, 'interval', minutes=15, id='all_collectors_job', replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started.")
