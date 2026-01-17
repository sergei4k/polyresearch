# PolyResearch - 20-Hour Build Approach

## Executive Summary
Build a web application that provides Polymarket insights using public APIs. Focus on speed and core features.

## Tech Stack (Speed-Optimized)

**Backend**: FastAPI (Python)
- Fast to develop
- Auto-generated API docs
- Async support
- You already have Python scripts

**Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- Server-side rendering
- Fast development
- Modern UI components
- Easy deployment on Vercel

**Database**: SQLite (optional caching)
- No setup needed
- Simple file-based
- Good enough for MVP

## Time Breakdown (20 Hours)

### Phase 1: Backend Foundation (4 hours)
**Hour 1-2: Setup & Core API**
- Set up FastAPI project structure
- Create Polymarket API client (reuse existing code)
- Health check endpoint
- Basic error handling

**Hour 3-4: Top Gainers Endpoint**
- Port `find_top_gainers.py` to FastAPI service
- Create `/api/top-gainers` endpoint
- Add caching layer (SQLite)
- Test and document

### Phase 2: Markets APIs (4 hours)
**Hour 5-6: Markets to Watch**
- Create `/api/markets/watch` endpoint
- Implement scoring algorithm:
  - Volume growth (24h vs 1wk)
  - Recent creation (< 7 days)
  - High liquidity (> $10k)
  - Competitive (30-70% probability)
- Sort by score

**Hour 7-8: Trending & Volume Leaders**
- `/api/markets/trending` - highest 24h volume
- `/api/markets/volume-leaders` - top by period (24h/1wk/1mo)
- Search endpoint `/api/markets/search`

### Phase 3: Frontend Setup (4 hours)
**Hour 9-10: Project Setup**
- Initialize Next.js 14 project
- Configure Tailwind CSS
- Set up TypeScript types
- Create API client utilities

**Hour 11-12: Layout & Navigation**
- Create main layout component
- Header with navigation
- Responsive design
- Loading states component

### Phase 4: Dashboard Components (6 hours)
**Hour 13-14: Top Gainers Component**
- Fetch and display top gainers table
- Show wallet, gain, trade count
- Auto-refresh every 5 minutes
- Link to wallet on Polymarket

**Hour 15-16: Markets to Watch Component**
- Display scored markets
- Show reasons (why it's worth watching)
- Links to Polymarket markets
- Volume and liquidity metrics

**Hour 17-18: Trending Markets Component**
- List trending markets
- Volume charts (using Recharts)
- Sortable columns
- Quick stats cards

### Phase 5: Polish & Deploy (2 hours)
**Hour 19: Polish**
- Error handling
- Loading states
- Responsive design checks
- UI refinements

**Hour 20: Deploy**
- Deploy backend (Railway/Render - free tier)
- Deploy frontend (Vercel - free tier)
- Test live deployment
- Update environment variables

## Core Features (MVP)

### 1. Top Gainers Dashboard
- Table showing top 20 new account gainers
- Columns: Wallet, Gain (USD), Trades, Time Period
- Auto-refresh toggle

### 2. Markets to Watch
- Scored list of markets worth watching
- Shows reasons: "2.5x volume growth", "Created 3 days ago", etc.
- Link to Polymarket market page

### 3. Trending Markets
- Top markets by 24h volume
- Simple chart showing volume comparison
- Sortable by volume, liquidity, comments

### 4. Search
- Basic search by market title/slug
- Quick results display

## File Structure (Minimal)

```
PolyResearch/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── api/
│   │   │   ├── routes.py        # All endpoints
│   │   │   └── polymarket.py    # API client
│   │   └── services/
│   │       ├── top_gainers.py   # Top gainers logic
│   │       └── markets.py       # Market analysis
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Main dashboard
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── TopGainers.tsx
│   │   │   ├── MarketsWatch.tsx
│   │   │   └── TrendingMarkets.tsx
│   │   └── lib/
│   │       └── api.ts           # API client
│   └── package.json
└── README.md
```

## API Endpoints (Essential Only)

```
GET  /api/health                    # Health check
GET  /api/top-gainers?hours=24&top_n=20
GET  /api/markets/watch?limit=20
GET  /api/markets/trending?limit=20
GET  /api/markets/volume-leaders?period=24h&limit=20
GET  /api/markets/search?q={query}
```

## Key Implementation Notes

### Backend Strategy
1. **Reuse existing code** - Port `find_top_gainers.py` directly
2. **Simple caching** - SQLite with 5-minute TTL
3. **Error handling** - Return empty arrays on failure, don't crash
4. **Rate limiting** - Add simple in-memory rate limiter

### Frontend Strategy
1. **Server Components** - Use Next.js 14 server components for data fetching
2. **Static pages where possible** - Revalidate every 60 seconds
3. **Progressive enhancement** - Works without JS for basic display
4. **Minimal dependencies** - Only add what's needed

### Data Flow
```
User Request → Next.js (Server Component)
                ↓
            FastAPI Backend
                ↓
            Polymarket API
                ↓
            SQLite Cache (optional)
                ↓
            Return to Frontend
```

## Scoring Algorithm (Markets to Watch)

```python
score = 0
reasons = []

# Volume growth (weight: 30)
if volume_24h / volume_1wk > 2:
    score += 30
    reasons.append(f"{growth_ratio:.1f}x volume growth")

# Recent creation (weight: 20)
if created_days_ago <= 7:
    score += 20
    reasons.append(f"Created {days} days ago")

# High liquidity (weight: 15)
if liquidity > 10000:
    score += 15
    reasons.append("High liquidity")

# Competitive market (weight: 25)
if 0.3 <= max_probability <= 0.7:
    score += 25
    reasons.append("Competitive market")

# High volume (weight: 10)
if volume_24h > 50000:
    score += 10
    reasons.append("High volume")
```

## Deployment Strategy

### Backend (Railway/Render)
1. Push to GitHub
2. Connect to Railway/Render
3. Set environment variables
4. Deploy (auto-deploys on push)

### Frontend (Vercel)
1. Push to GitHub
2. Import to Vercel
3. Set `NEXT_PUBLIC_API_URL` environment variable
4. Deploy (auto-deploys on push)

## Risk Mitigation

### Time Overruns
- **If behind on backend**: Skip caching, implement later
- **If behind on frontend**: Use simpler UI (no charts, just tables)
- **If behind overall**: Focus on Top Gainers + Markets to Watch only

### API Limitations
- Polymarket API may rate limit
- Solution: Add retry logic, increase cache TTL
- Fallback: Show cached data with "last updated" timestamp

### Deployment Issues
- Use simpler deployment (Vercel API routes instead of separate backend)
- Or deploy backend to Fly.io (easier than Railway)

## Success Criteria

By end of 20 hours, you should have:
✅ Working website accessible online
✅ Top gainers showing real data
✅ Markets to watch with scores
✅ Trending markets list
✅ Basic search functionality
✅ Responsive design
✅ Deployed and live

## Post-20-Hour Enhancements

If you have extra time or want to iterate:
- Add charts/graphs
- Market details page
- User favorites/watchlist
- Email alerts
- Historical data
- More advanced analytics

## Quick Start Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Visit http://localhost:3000
```

## Key Principles

1. **Ship fast** - MVP first, polish later
2. **Reuse code** - Leverage existing scripts
3. **Keep it simple** - No over-engineering
4. **Focus on value** - Core features only
5. **Test as you go** - Don't wait until end
