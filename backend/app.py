from flask import Flask, request, jsonify

from fetch_polymarket import fetch_event_by_slug


app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/api/filter_markets', methods=['POST'])
def get_event_data():
    # Get JSON data from the request
    data = request.get_json()
    
    # Access individual fields
    market = data.get('market')
    days = data.get('days')
    money_gain = data.get('moneyGain')
    money_lost = data.get('moneyLost')
    total_money_spent = data.get('totalMoneySpent')
    trades_condition = data.get('tradesCondition')
    trades_count = data.get('tradesCount')
    user_name_visibility = data.get('userNameVisibility')
    
    print(f"Received filter request: {data}")
    
    # Return a response
    return jsonify({'status': 'success', 'received': data})
    


if __name__ == '__main__':
    app.run(debug=True)


