# PolyResearch Project Memory

## Project Overview

**PolyWatcher** (branded as PolyResearch) is an analytics engine designed to detect "Smart Money" and potential insider trading activity on Polymarket prediction markets. The tool correlates data from Polymarket's APIs to identify wallets that trade with "unnatural conviction" - positions taken shortly before market-moving news or with asymmetric risk profiles.

### Core Philosophy
Prediction markets are often the first place "the truth" appears before mainstream news. PolyWatcher monitors the Polymarket order book and public profiles to flag accounts that match the signature of informed traders who may have material non-public information (MNPI).

## Architecture

### Tech Stack
- **Backend**: Python Flask API
- **Frontend**: Next.js 16 (React 19) with TypeScript
- **Styling**: Tailwind CSS with next-themes for dark mode
- **APIs**: Polymarket Gamma API (market data) and Data API (trades/activity)

### Project Structure
```
polyresearch/
├── backend/
│   ├── app.py                    # Flask API server
│   ├── fetch_polymarket.py       # Fetch market events by slug
│   ├── find_top_gainers.py       # Identify high-gain new accounts
│   ├── services/
│   │   ├── markets.py            # Markets service (Gamma API)
│   │   └── gainers.py            # Gainers tracking service
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # Environment variables
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx          # Main UI with filters
    │   │   └── api/filter/route.ts  # API route
    │   └── components/
    │       ├── chat-component.tsx    # Chat interface
    │       └── theme-provider.tsx    # Theme management
    └── package.json              # Node dependencies
```

## Backend Components

### 1. Flask API (`app.py`)
- **Purpose**: REST API server connecting frontend to Polymarket data
- **Endpoints**:
  - `GET /` - Health check
  - `POST /api/filter_markets` - Filter markets based on user criteria
- **Status**: Basic implementation, endpoint receives filters but doesn't process yet

### 2. Market Fetcher (`fetch_polymarket.py`)
- **Purpose**: Fetch event data from Polymarket by slug
- **API**: Polymarket Gamma API (`https://gamma-api.polymarket.com`)
- **Features**:
  - Fetch events by slug or ID
  - Parse and format market probabilities
  - Display candidates/outcomes with volume data
  - Save raw JSON responses
- **Example**: Fetches "Who will Trump nominate as Fed Chair?" event

### 3. Top Gainers Tracker (`find_top_gainers.py`)
- **Purpose**: Identify new accounts with largest gains
- **API**: Polymarket Data API (`https://data-api.polymarket.com`)
- **Key Features**:
  - Fetch recent trades (configurable time window: 24h, 30d, etc.)
  - Approximate "new accounts" by first trade timestamp
  - Calculate gains: `(SELL proceeds) - (BUY costs)`
  - Track both trade-based and activity-based gains
  - Output top N gainers to console and JSON

**Algorithm**:
1. Fetch trades from last N hours (default 720 = 30 days)
2. Extract unique wallets
3. Identify wallets whose first trade is within window
4. Calculate gain for each wallet
5. Sort by gain, return top N

**Limitations**:
- Cannot truly verify account creation date (API doesn't expose it)
- Only tracks realized gains (not unrealized positions)
- Doesn't account for market resolution
- May be rate-limited for large datasets

### 4. Services Layer

#### `services/markets.py`
- **Purpose**: Abstracted service for market operations
- **Methods**:
  - `get_market_by_slug(slug)` - Fetch specific market
  - `get_trending_markets(period, limit)` - Get trending markets by volume
  - `get_markets_to_watch(limit)` - Recommended markets
  - `search_markets(query, limit)` - Search markets by text

#### `services/gainers.py`
- **Purpose**: Modular gainers tracking (refactored from `find_top_gainers.py`)
- **Methods**:
  - `get_recent_trades(hours, limit)` - Fetch trades
  - `get_user_activity(user, limit)` - Fetch user activity
  - `is_new_account(wallet, cutoff_time, trades)` - Check if new
  - `calculate_gain_from_trades(wallet, trades)` - Trade-based gains
  - `calculate_gain_from_activity(wallet, activities)` - Activity-based gains
  - `find_top_gainers(hours, limit, min_profit, sort_by)` - Main API

**Parameters for filtering**:
- `hours`: Lookback period
- `limit`: Max results
- `min_profit`: Minimum profit threshold
- `sort_by`: 'profit', 'trades', or 'activity_gain'

## Frontend Components

### 1. Main Page (`page.tsx`)
- **Type**: Client component ("use client")
- **Features**:
  - Market selection dropdown (Trending, Breaking, Politics, Sports, etc.)
  - Timeframe selector (1-7 days)
  - Money filters:
    - Money Gain (min $)
    - Money Lost (min $)
    - Total Money Spent (min $)
  - Trade count filter (< less / > more than N trades)
  - User name visibility filter (hidden/public)
  - "Apply" button to submit filters
- **State Management**: Local React useState hooks
- **API Integration**: POSTs to `/api/filter` endpoint
- **UI/UX**:
  - Three-column layout (sidebar stats, main content, filters)
  - Loading states with spinner
  - Custom increment/decrement controls

### 2. Chat Component (`chat-component.tsx`)
- **Type**: Client component
- **Purpose**: AI chat interface (not yet integrated in main page)
- **Features**:
  - Message history (user/bot)
  - Send messages to `/api/chat` endpoint
  - Loading states
  - Error handling
- **Status**: Component exists but `/api/chat` endpoint not implemented

### 3. Theme Provider (`theme-provider.tsx`)
- **Purpose**: Dark/light mode support via next-themes
- **Status**: Integrated but UI doesn't show theme toggle yet

## API Endpoints

### Polymarket APIs Used

#### 1. Gamma API (Market Data)
- **Base**: `https://gamma-api.polymarket.com`
- **Endpoints**:
  - `GET /events` - List events (with query params)
  - `GET /events/slug/{slug}` - Get event by slug
  - `GET /events/{id}` - Get event by ID
- **Data**: Event metadata, markets, outcomes, probabilities, volume, liquidity

#### 2. Data API (Trades & Activity)
- **Base**: `https://data-api.polymarket.com`
- **Endpoints**:
  - `GET /trades` - Recent trades (timestamp filter)
  - `GET /activity` - User activity (may be restricted)
- **Data**: Trade executions, wallet addresses, buy/sell sides, prices, sizes

## Data Flow

### Filter Markets Flow (Planned)
```
User Input (Frontend)
  → POST /api/filter_markets (Flask)
  → services/gainers.find_top_gainers(...)
  → Filter results based on criteria
  → Return filtered wallets/traders
  → Frontend displays results
```

### Current Implementation Status
- ✅ Frontend UI complete with all filters
- ✅ Backend services (markets, gainers) implemented
- ⚠️ Flask endpoint receives data but doesn't process
- ❌ Integration between frontend filters and backend logic incomplete
- ❌ Chat functionality not implemented

## Key Metrics & Filters

The UI allows filtering traders by:

1. **Market Category**: Trending, Breaking, New, Politics, Sports, Crypto, Finance, Geopolitics, Tech, etc.
2. **Timeframe**: 1-7 days
3. **Profit Metrics**:
   - Money gained (min threshold)
   - Money lost (max threshold)
   - Total money spent (min/max)
4. **Activity Metrics**:
   - Number of trades (< less than or > more than N)
5. **Privacy**:
   - Show only public profiles or include hidden usernames

## Dependencies

### Backend (Python)
```
flask >= 3.0.0
flask-cors >= 4.0.0
requests >= 2.31.0
google-generativeai >= 0.3.0  # For AI features (not yet used)
```

### Frontend (Node.js)
```json
{
  "lucide-react": "^0.562.0",     // Icons
  "next": "16.1.3",               // Framework
  "next-themes": "^0.4.6",        // Theme support
  "react": "19.2.3",
  "react-dom": "19.2.3",
  "tailwindcss": "^3.4.19"        // Styling
}
```

## Git Status (at memory creation)
- Branch: `spencer`
- Main branch: `main`
- Modified files:
  - `README.md`
  - `backend/polymarket_event_data.json`
- Untracked: `backend/__pycache__/fetch_polymarket.cpython-313.pyc`
- Recent commits:
  - f1bf120 "flask setup"
  - eccdb10 "AAAAAA"
  - 646609c "asd"
  - 41a807b "BACK END"

## Development Commands

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py  # Start Flask server on http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # Start Next.js dev server on http://localhost:3000
```

### Standalone Scripts
```bash
cd backend
python fetch_polymarket.py          # Fetch sample event data
python find_top_gainers.py          # Run top gainers analysis
```

## Next Steps / TODOs

### Critical
1. **Connect Frontend to Backend**:
   - Update frontend `/api/filter` route to call Flask backend
   - Or implement filtering logic in Next.js API route
   - Handle CORS if needed

2. **Implement Filter Logic**:
   - Connect filter parameters to `gainers.find_top_gainers()`
   - Filter by market category
   - Apply profit/loss thresholds
   - Filter by trade count
   - Filter by username visibility

3. **Display Results**:
   - Design results table/cards in main content area
   - Show wallet addresses, gains, trade count
   - Link to Polymarket profiles

### Nice to Have
4. **Chat Integration**:
   - Implement `/api/chat` endpoint
   - Connect to AI (Google Gemini per dependencies)
   - Allow natural language queries

5. **Real-time Updates**:
   - WebSocket or polling for live data
   - Auto-refresh top gainers

6. **Enhanced Analytics**:
   - Win rate calculation
   - Market-specific performance
   - Time-series charts

7. **User Profiles**:
   - Deep dive into specific wallet activity
   - Transaction history
   - Portfolio analysis

## Important Notes

### API Limitations
- Polymarket APIs are public but may have rate limits
- Account creation dates not available (approximated by first trade)
- Activity endpoint may be restricted for some users

### Ethical Considerations
- Tool designed for transparency and research
- "Insider trading" detection is speculative
- Users should verify findings independently
- Not financial advice

### Performance
- Checking hundreds of wallets can take minutes
- Consider caching, async requests, or background jobs
- Frontend should show loading states

## File Locations Reference
- Backend Python files: `/Users/spencerstuff/repos/polyresearch/backend/`
- Frontend source: `/Users/spencerstuff/repos/polyresearch/frontend/src/`
- Sample output: `backend/top_gainers_24h.json`, `backend/top_gainers_30d.json`
- Raw market data: `backend/polymarket_event_data.json`
