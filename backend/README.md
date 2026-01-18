# Polymarket Data Fetcher

This script fetches event data from Polymarket's public API (Gamma API) as part of the Polymarket Builders Program.

## Event

Fetches data for: **"Who will Trump nominate as Fed Chair?"**

Event URL: https://polymarket.com/event/who-will-trump-nominate-as-fed-chair

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python fetch_polymarket.py
```

The script will:
1. Fetch event data from Polymarket's Gamma API using the event slug
2. Display formatted event information (title, dates, volume, outcomes, probabilities)
3. Save raw JSON data to `polymarket_event_data.json`

## API Information

This uses the Polymarket Gamma API (public API for the Builders Program):

- **Endpoint**: `https://gamma-api.polymarket.com/events/slug/{slug}`
- **Documentation**: https://docs.polymarket.com/

## Output

The script displays:
- Event metadata (title, slug, ID, dates, volume, liquidity)
- Markets and outcomes
- Outcome probabilities (implied from prices)
- Trading volumes per outcome

Raw JSON response is saved to `polymarket_event_data.json` for further processing.
