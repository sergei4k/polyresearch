# PolyResearch - 20-Hour Build Approach

## Overview
A web application that provides insights into Polymarket data, including top gainers, markets to watch, trending markets, and more.

## Tech Stack (Optimized for Speed)

### Backend
- **FastAPI** - Fast, modern Python framework with automatic API docs
- **Python 3.9+** - Already have scripts written in Python
- **SQLite** - Simple database for caching (no setup needed)
- **Requests** - HTTP client (already using)

### Frontend
- **Next.js 14** (React) - Server-side rendering, fast development
- **Tailwind CSS** - Quick styling without custom CSS
- **Recharts** - Charts for data visualization
- **TypeScript** - Type safety

### Alternative (Even Faster - Full Python Stack)
- **Flask** + **Jinja2** - Simpler, single language stack
- **Bootstrap** or **Tailwind CDN** - Quick styling

**We'll go with the Next.js + FastAPI approach for better scalability.**

## Project Structure

```
PolyResearch/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py        # API endpoints
│   │   │   └── polymarket.py    # Polymarket API client
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── top_gainers.py   # Top gainers logic
│   │   │   └── markets.py       # Market analysis
│   │   └── models/
│   │       └── schemas.py       # Pydantic models
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js app directory
│   │   │   ├── page.tsx         # Main dashboard
│   │   │   ├── layout.tsx
│   │   │   └── api/             # API routes (if needed)
│   │   ├── components/
│   │   │   ├── TopGainers.tsx
│   │   │   ├── MarketsWatch.tsx
│   │   │   ├── TrendingMarkets.tsx
│   │   │   └── VolumeLeaders.tsx
│   │   ├── lib/
│   │   │   └── api.ts           # API client
│   │   └── types/
│   │       └── polymarket.ts    # TypeScript types
│   ├── package.json
│   └── next.config.js
├── shared/                       # Shared utilities
│   └── find_top_gainers.py      # Existing script
├── README.md
└── docker-compose.yml           # Optional for deployment
```

## Feature List (Prioritized)

### Phase 1: Core Features (8 hours)
1. **Top Gainers Dashboard** (2 hours)
   - Reuse existing `find_top_gainers.py` script
   - Display table of top 20 gainers
   - Show wallet addresses, gains, trade counts
   - Auto-refresh every 5 minutes

2. **Markets to Watch** (3 hours)
   - High volume growth (24h vs 1wk)
   - High price movement (probability changes)
   - New markets (created in last 24h)
   - Sorting/filtering options

3. **Trending Markets** (2 hours)
   - Markets with highest 24h volume
   - Markets with most price movement
   - Quick links to Polymarket

4. **Basic UI/UX** (1 hour)
   - Clean, modern dashboard
   - Responsive design
   - Loading states

### Phase 2: Enhanced Features (6 hours)
5. **Volume Leaders** (2 hours)
   - Top markets by volume (24h, 1wk, 1mo)
   - Volume growth charts
   - Market categories

6. **Market Details Page** (2 hours)
   - Individual market analysis
   - Price history (if available)
   - Outcome probabilities
   - Trading activity

7. **Search & Filters** (2 hours)
   - Search markets by title
   - Filter by category/tags
   - Date range filtering

### Phase 3: Polish & Deploy (6 hours)
8. **Performance Optimization** (2 hours)
   - Caching layer (SQLite/Redis)
   - API rate limiting
   - Lazy loading

9. **Additional Insights** (2 hours)
   - Most competitive markets (close to 50/50)
   - Biggest movers (probability swings)
   - New account activity trends

10. **Deployment** (2 hours)
    - Vercel (frontend) + Railway/Render (backend)
    - Environment variables
    - Domain setup (optional)

## Time Breakdown

### Hour 1-2: Setup & Backend Foundation
- Set up FastAPI project
- Create API structure
- Integrate Polymarket API client
- Basic health check endpoint

### Hour 3-4: Top Gainers API
- Port `find_top_gainers.py` to FastAPI service
- Create `/api/top-gainers` endpoint
- Add caching (SQLite)
- Test endpoint

### Hour 5-7: Markets API
- Create `/api/markets/watch` endpoint
- Implement market analysis logic
- Create `/api/markets/trending` endpoint
- Volume calculations

### Hour 8-10: Frontend Setup
- Initialize Next.js project
- Set up Tailwind CSS
- Create layout and routing
- API client setup

### Hour 11-13: Dashboard Components
- Top Gainers component
- Markets to Watch component
- Trending Markets component
- Basic styling

### Hour 14-16: Enhanced Features
- Market details page
- Search functionality
- Filters and sorting
- Charts for visualization

### Hour 17-18: Polish & UX
- Loading states
- Error handling
- Responsive design
- Performance optimization

### Hour 19-20: Deployment
- Set up deployment configs
- Deploy backend
- Deploy frontend
- Testing and fixes

## API Endpoints

```
GET  /api/health                    # Health check
GET  /api/top-gainers               # Top gainers in last 24h
GET  /api/markets/watch             # Markets to watch
GET  /api/markets/trending          # Trending markets
GET  /api/markets/volume-leaders    # Volume leaders
GET  /api/markets/{slug}            # Market details
GET  /api/markets/search?q={query}  # Search markets
```

## Data Sources

1. **Polymarket Gamma API** - Event/market data
   - `https://gamma-api.polymarket.com/events`
   - `https://gamma-api.polymarket.com/events/slug/{slug}`

2. **Polymarket Data API** - Trading data
   - `https://data-api.polymarket.com/trades`
   - `https://data-api.polymarket.com/activity`

## Key Insights to Display

### Markets to Watch Criteria
1. **High Volume Growth**: `volume24hr / volume1wk` ratio > 2x
2. **Recent Creation**: Created in last 7 days
3. **High Liquidity**: Liquidity > $10k
4. **Price Movement**: Outcome price changes > 10% in 24h
5. **Competitive**: Outcome prices between 30-70% (uncertain)

### Trending Markets Criteria
1. Highest 24h volume
2. Most comments (engagement)
3. Highest price movement
4. Recent activity spikes

## Database Schema (SQLite)

```sql
CREATE TABLE cache_top_gainers (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER,
    data TEXT,  -- JSON
    UNIQUE(timestamp)
);

CREATE TABLE cache_markets (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE,
    data TEXT,  -- JSON
    updated_at INTEGER
);

CREATE TABLE market_snapshots (
    id INTEGER PRIMARY KEY,
    slug TEXT,
    price REAL,
    volume REAL,
    timestamp INTEGER
);
```

## Quick Start Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Deployment Options

### Option 1: Vercel + Railway (Recommended)
- Frontend: Vercel (free, automatic)
- Backend: Railway/Render (free tier)

### Option 2: Vercel Full-Stack
- Use Next.js API routes for backend
- Single deployment on Vercel
- Simpler but less flexible

### Option 3: Docker Compose
- Self-hosted solution
- Good for local development

## Success Metrics

By end of 20 hours, you should have:
- ✅ Working dashboard showing top gainers
- ✅ Markets to watch feature
- ✅ Trending markets display
- ✅ Search functionality
- ✅ Deployed and accessible online
- ✅ Clean, responsive UI

## Future Enhancements (Post 20h)

- User accounts and watchlists
- Email alerts for price movements
- Historical data and charts
- API for third-party integration
- Mobile app
- Advanced analytics and predictions
