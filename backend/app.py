from flask import Flask, request, jsonify
from flask_cors import CORS

from fetch_polymarket import fetch_event_by_slug
from services.gainers import GainersService
from services.markets import MarketsService


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize services
gainers_service = GainersService()
markets_service = MarketsService()


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/api/filter_markets', methods=['POST'])
def filter_markets():
    """
    Filter and fetch top profiles from Polymarket based on user-defined filters.
    Returns top 10 profiles matching the criteria.
    """
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Access individual fields
        market = data.get('market', 'Trending')
        days = data.get('days', 1)
        money_gain = data.get('moneyGain', 0)
        money_lost = data.get('moneyLost', 0)
        total_money_spent = data.get('totalMoneySpent', 0)
        trades_condition = data.get('tradesCondition', 'less')
        trades_count = data.get('tradesCount', 0)
        user_name_visibility = data.get('userNameVisibility', 'public')

        print(f"Received filter request: {data}")
        print(f"Filter: {trades_condition} than {trades_count} trades")

        # Convert days to hours for the API
        hours = days * 24

        # Fetch top gainers based on timeframe
        print(f"Fetching gainers for {hours} hours...")
        gainers = gainers_service.find_top_gainers(
            hours=hours,
            limit=50,  # Fetch more than needed for filtering
            min_profit=money_gain if money_gain > 0 else 0
        )

        # Apply filters
        filtered_profiles = []
        for gainer in gainers:
            # Filter by money gain (profit)
            if money_gain > 0 and gainer.get('profit', 0) < money_gain:
                continue

            # Filter by money lost (negative profit)
            # Note: loss would be negative profit, but since we're tracking gains,
            # we'll skip this filter or interpret it differently

            # Filter by trades count
            trade_count = gainer.get('trades', 0)
            if trades_condition == 'less' and trade_count >= trades_count:
                continue
            elif trades_condition == 'more' and trade_count <= trades_count:
                continue

            # Filter by total money spent
            # Note: We don't have direct "total spent" in current data
            # We can approximate with trade_gain calculations or skip

            filtered_profiles.append({
                'wallet': gainer.get('wallet'),
                'profit': round(gainer.get('profit', 0), 2),
                'trades': gainer.get('trades', 0),
                'trade_gain': round(gainer.get('trade_gain', 0), 2),
                'activity_gain': round(gainer.get('activity_gain', 0), 2),
                'activity_count': gainer.get('activity_count', 0)
            })

        # Sort by profit and take top 10
        filtered_profiles.sort(key=lambda x: x['profit'], reverse=True)
        top_10 = filtered_profiles[:10]

        print(f"Total filtered: {len(filtered_profiles)}, Returning top {len(top_10)} profiles")

        return jsonify({
            'status': 'success',
            'count': len(top_10),
            'profiles': top_10
        })

    except Exception as e:
        print(f"Error processing filter request: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)


