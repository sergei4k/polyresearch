# Polymarket Top Gainers Tracker

This script identifies accounts with the **largest gains** among **new accounts** in the last 24 hours on Polymarket.

## What It Does

1. **Fetches recent trades** from Polymarket's Data API (last 24 hours)
2. **Identifies new accounts** by checking if their first trade occurred in the last 24 hours
3. **Calculates gains** for each new account based on their trading activity
4. **Displays top gainers** sorted by highest gains

## Features

- ✅ Automatic detection of new accounts (approximated by first trade timestamp)
- ✅ Gain calculation based on BUY/SELL trades
- ✅ Saves results to JSON file for further analysis
- ✅ Progress indicators for long-running operations
- ✅ Handles API errors gracefully

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python find_top_gainers.py
```

The script will:
1. Fetch trades from the last 24 hours
2. Identify accounts whose first trade was in that window
3. Calculate gains for those accounts
4. Display the top 20 gainers
5. Save detailed results to `top_gainers_24h.json`

## Output

### Console Output
```
🚀 Polymarket Top Gainers Tracker
====================================================================================================

Rank   Wallet                                        Gain (USD)      Trades   Activities
====================================================================================================
1      0x204f72f35326db932158cba6adff0b9a1da95e14    $   14,534.23 17       100       
2      0x987069e3ba77f73bc43fcad0dd43fa3eced7b9d3    $    5,199.38 2        100       
...
```

### JSON Output
Results are saved to `top_gainers_24h.json` with:
- Timestamp of analysis
- Period analyzed (24 hours)
- Detailed results for each account:
  - Wallet address
  - Total gain (USD)
  - Trade-based gain
  - Activity-based gain
  - Number of trades
  - Number of activities

## How It Works

### New Account Detection

Since Polymarket's API doesn't expose account creation dates, the script uses this approach:

1. **Fetches all trades** from the last 24 hours
2. **Extracts unique wallets** from those trades
3. **For each wallet**, finds their earliest trade in the dataset
4. **If earliest trade is within 24 hours**, considers it a "new account"

**Note**: This is an approximation. A truly new account would have no trades before the 24-hour window, but the API only returns recent trades. This method identifies wallets that **started trading** in the last 24 hours.

### Gain Calculation

The script calculates gains using two methods and uses the higher value:

1. **Trade-based gain**: 
   - Proceeds from SELL trades minus costs from BUY trades
   - Formula: `(Sum of SELL prices × sizes) - (Sum of BUY prices × sizes)`

2. **Activity-based gain** (if available):
   - Sums REDEEM activities (realized gains from winning positions)
   - Accounts for TRADE activities

## Limitations & Caveats

### 1. Account Detection
- **Not perfect**: The script can only see trades from the last 24 hours
- **False positives**: Accounts that haven't traded in a while but resumed trading may be marked as "new"
- **Cannot verify**: We can't check if accounts existed before the window without historical data

### 2. Gain Calculation
- **Realized vs Unrealized**: Only counts realized gains from trades (SELL proceeds minus BUY costs)
- **Open positions**: Doesn't account for unrealized gains from open positions
- **Market resolution**: Doesn't check if markets have resolved (for calculating true P&L)

### 3. API Limitations
- **Rate limits**: The script makes many API calls; may be rate-limited
- **Activity endpoint**: The `/activity` endpoint may be restricted for some users
- **Data availability**: Some data may not be publicly accessible

### 4. Performance
- **Processing time**: Checking hundreds of wallets can take several minutes
- **Network dependency**: Requires stable internet connection

## Customization

### Change Time Window

Edit the `main()` function:

```python
top_gainers = tracker.find_top_gainers(hours=48, top_n=20)  # Last 48 hours
```

### Change Number of Top Gainers

```python
top_gainers = tracker.find_top_gainers(hours=24, top_n=50)  # Top 50 instead of 20
```

### Change Trade Limit

Edit the `get_recent_trades()` method:

```python
trades = self.get_recent_trades(hours=hours, limit=5000)  # Fetch more trades
```

## API Endpoints Used

- **Trades**: `GET https://data-api.polymarket.com/trades`
- **Activity** (if available): `GET https://data-api.polymarket.com/activity?user={wallet}`

## Example Output

```json
{
  "timestamp": "2026-01-17T20:00:00+00:00",
  "period_hours": 24,
  "results": [
    {
      "wallet": "0x204f72f35326db932158cba6adff0b9a1da95e14",
      "gain": 14534.23,
      "trade_gain": 14534.23,
      "activity_gain": 0.0,
      "trade_count": 17,
      "activity_count": 100
    },
    ...
  ]
}
```

## Troubleshooting

### No Results Found
- **Check API availability**: The Polymarket Data API may be down
- **Try increasing time window**: Maybe no new accounts in exactly 24 hours
- **Check rate limits**: Too many requests may be blocked

### All Accounts Marked as "New"
- This can happen if all wallets in the dataset have trades only within the 24-hour window
- This is expected behavior if the API only returns recent trades

### Slow Performance
- The script checks each wallet individually
- For hundreds of wallets, this can take several minutes
- Consider reducing the number of wallets to check or using async requests

## Future Improvements

Potential enhancements:
- [ ] Use async requests for faster processing
- [ ] Cache wallet data to avoid repeated API calls
- [ ] Integrate with market resolution data for accurate P&L
- [ ] Add support for filtering by market/event
- [ ] Export to CSV format
- [ ] Add command-line arguments for customization
