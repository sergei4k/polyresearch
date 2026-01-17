# PolyResearch Flask Backend

Simple Flask API for Polymarket insights with filtering support.

## Setup

```bash
cd flask_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

API runs at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /api/health
```

### Top Gainers
```
GET /api/gainers

Query params:
  hours        - Time period in hours (1-720, default: 24)
  min_profit   - Minimum profit filter (default: 0)
  max_profit   - Maximum profit filter (optional)
  min_trades   - Minimum trade count (default: 0)
  max_trades   - Maximum trade count (optional)
  sort_by      - Sort by: profit, trades, activity_gain (default: profit)
  sort_order   - Sort direction: asc, desc (default: desc)
  limit        - Number of results (1-100, default: 20)
  offset       - Pagination offset (default: 0)

Examples:
  /api/gainers?hours=48&min_profit=1000
  /api/gainers?hours=168&sort_by=trades&sort_order=asc
  /api/gainers?min_trades=5&max_trades=50&limit=50
```

### Markets to Watch
```
GET /api/markets/watch

Query params:
  limit         - Number of results (1-50, default: 20)
  min_score     - Minimum score threshold (default: 0)
  min_volume    - Minimum 24h volume (default: 0)
  min_liquidity - Minimum liquidity (default: 0)
  created_days  - Only markets created within N days (optional)

Examples:
  /api/markets/watch?min_score=50
  /api/markets/watch?created_days=7&min_liquidity=10000
```

### Trending Markets
```
GET /api/markets/trending

Query params:
  period     - Time period: 24h, 1wk, 1mo (default: 24h)
  limit      - Number of results (1-50, default: 20)
  min_volume - Minimum volume threshold (default: 0)

Examples:
  /api/markets/trending?period=1wk
  /api/markets/trending?min_volume=100000
```

### Search Markets
```
GET /api/markets/search

Query params:
  q     - Search query (required)
  limit - Number of results (1-50, default: 20)

Examples:
  /api/markets/search?q=trump
  /api/markets/search?q=bitcoin&limit=10
```

### Market Details
```
GET /api/markets/<slug>

Examples:
  /api/markets/who-will-trump-nominate-as-fed-chair
```

## Response Format

All endpoints return JSON:

```json
{
  "filters": { ... },
  "count": 20,
  "timestamp": "2026-01-17T20:00:00+00:00",
  "results": [ ... ]
}
```

## Scoring Algorithm (Markets to Watch)

Markets are scored on a 0-100 scale based on:

| Criteria | Points | Condition |
|----------|--------|-----------|
| Volume growth | 30 | 24h/1wk volume ratio > 2x |
| Recent creation | 20 | Created within 7 days |
| High liquidity | 15 | Liquidity > $10,000 |
| Competitive | 25 | Max probability 30-70% |
| High volume | 10 | 24h volume > $50,000 |
