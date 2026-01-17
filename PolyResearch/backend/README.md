# PolyResearch Backend

FastAPI backend for Polymarket insights.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`

API docs at `http://localhost:8000/docs`

## Endpoints

- `GET /api/health` - Health check
- `GET /api/top-gainers` - Top gainers in last N hours
- `GET /api/markets/watch` - Markets to watch
- `GET /api/markets/trending` - Trending markets
- `GET /api/markets/volume-leaders` - Volume leaders
- `GET /api/markets/{slug}` - Market details
- `GET /api/markets/search?q={query}` - Search markets
