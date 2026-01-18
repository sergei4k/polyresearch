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
        market = data.get('market', None)  # None = all markets
        hours = data.get('hours', 1)
        money_gain = data.get('moneyGain', 0)
        money_gain_condition = data.get('moneyGainCondition', 'reset')
        money_lost = data.get('moneyLost', 0)
        money_lost_condition = data.get('moneyLostCondition', 'reset')
        total_money_spent = data.get('totalMoneySpent', 0)
        total_money_spent_condition = data.get('totalMoneySpentCondition', 'reset')
        trades_condition = data.get('tradesCondition', 'reset')
        trades_count = data.get('tradesCount', 0)
        user_name_visibility = data.get('userNameVisibility', 'public')
        account_age_hours = data.get('accountAgeHours', 0)
        account_age_condition = data.get('accountAgeCondition', 'reset')

        print(f"Received filter request: {data}")
        print(f"Filter: {trades_condition} than {trades_count} trades")
        print(f"Market category: {market if market else 'All markets'}")

        # Fetch token IDs for the selected market category
        token_ids = None
        if market and market != 'All':
            print(f"Fetching markets for category: {market}")
            token_ids = markets_service.get_token_ids_for_category(market)
            print(f"Found {len(token_ids)} tokens in {market} category")
            if not token_ids:
                print(f"WARNING: No token IDs found for category '{market}' - this will return no results")
        else:
            print(f"No market filter - analyzing all markets")

        # Fetch top gainers based on timeframe and market filter
        print(f"Fetching gainers for {hours} hours...")
        if account_age_condition != 'reset' and account_age_hours > 0:
            account_age_days = account_age_hours / 24
            print(f"Filtering for accounts by age: {account_age_condition} than {account_age_days} days")
        gainers = gainers_service.find_top_gainers(
            hours=hours,
            limit=50,  # Fetch more than needed for filtering
            min_profit=0,  # Don't filter in the service, filter in app.py
            token_ids=token_ids,
            account_age_hours=account_age_hours,
            account_age_condition=account_age_condition
        )

        print(f"Received {len(gainers)} gainers from service")

        # Apply filters
        filtered_profiles = []
        filter_stats = {
            'total': len(gainers),
            'failed_money_gain': 0,
            'failed_money_lost': 0,
            'failed_total_spent': 0,
            'failed_trades': 0,
            'passed': 0
        }

        for gainer in gainers:
            # Filter by money gain (wins/profit)
            if money_gain_condition != 'reset':
                profit = gainer.get('profit', 0)
                if money_gain_condition == 'more' and profit <= money_gain:
                    filter_stats['failed_money_gain'] += 1
                    continue
                elif money_gain_condition == 'less' and profit >= money_gain:
                    filter_stats['failed_money_gain'] += 1
                    continue

            # Filter by money lost (losses)
            if money_lost_condition != 'reset':
                losses = gainer.get('losses', 0)
                if money_lost_condition == 'more' and losses <= money_lost:
                    filter_stats['failed_money_lost'] += 1
                    continue
                elif money_lost_condition == 'less' and losses >= money_lost:
                    filter_stats['failed_money_lost'] += 1
                    continue

            # Filter by total money spent
            if total_money_spent_condition != 'reset':
                spent = gainer.get('total_spent', 0)
                if total_money_spent_condition == 'more' and spent <= total_money_spent:
                    filter_stats['failed_total_spent'] += 1
                    continue
                elif total_money_spent_condition == 'less' and spent >= total_money_spent:
                    filter_stats['failed_total_spent'] += 1
                    continue

            # Filter by trades count
            if trades_condition != 'reset':
                trade_count = gainer.get('trades', 0)
                if trades_condition == 'more' and trade_count <= trades_count:
                    filter_stats['failed_trades'] += 1
                    continue
                elif trades_condition == 'less' and trade_count >= trades_count:
                    filter_stats['failed_trades'] += 1
                    continue

            filter_stats['passed'] += 1
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

        print(f"Filter results: {filter_stats}")
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


