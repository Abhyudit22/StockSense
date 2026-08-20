# StockSense 📈

**India Market Intelligence (NSE/BSE)**

StockSense is a real-time market intelligence dashboard designed for the Indian stock market. It automatically tracks popular NSE stocks, aggregates news and social media mentions, and performs AI-driven sentiment analysis to help you gauge whether the market is feeling Bullish, Bearish, or Neutral about specific companies.

## 🚀 Features

- **Live Sentiment Analysis:** Automatically scores incoming news articles and social media mentions using natural language processing.
- **Automated Data Collection:** Background workers run 24/7 to scrape the latest data from Google News, StockTwits, and other forums.
- **Real-Time Dashboard:** A beautiful, dark-mode SvelteKit frontend that displays overall market sentiment, active tracked stocks, and live intelligence feeds.
- **Market Indices:** Tracks live price changes for NIFTY 50, BANK NIFTY, and SENSEX.
- **Live Event Feed:** WebSocket integration streams real-time updates directly to your dashboard as the backend processes them.

## 🛠️ Tech Stack

**Frontend (Vercel)**
- [SvelteKit](https://kit.svelte.dev/) - UI Framework
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [TypeScript](https://www.typescriptlang.org/) - Language

**Backend (Railway)**
- [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) & [PostgreSQL](https://www.postgresql.org/) - Async database ORM and storage
- [Redis](https://redis.io/) - Caching and WebSocket pub/sub
- [APScheduler](https://apscheduler.readthedocs.io/) - Background task scheduling for data collection
- [NLTK (VADER) / FinBERT](https://www.nltk.org/) - Sentiment analysis engines

## ⚙️ Local Development Setup

### 1. Backend Setup
```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Create a .env file with your local database credentials
# Example: DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/stocksense
# Example: REDIS_URL=redis://localhost:6379

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create a .env file
# Example: VITE_API_URL=http://localhost:8000/api
# Example: VITE_WS_URL=ws://localhost:8000/ws/agent-feed

# Start the development server
npm run dev
```

## 🌐 Deployment Architecture
- The **Frontend** is designed to be hosted on serverless edge networks like **Vercel**.
- The **Backend** requires a continuous runtime environment like **Railway**, as it utilizes background threads and schedulers that run 24/7 to collect market data. 
- Ensure `CORS_ORIGINS` on the backend is strictly set to your frontend's production domain.

## 📝 License
MIT License
