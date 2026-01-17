"""
PolyResearch Flask Backend
Simple API for Polymarket insights with filtering support
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone

from services.gainers import GainersService
from services.markets import MarketsService

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# Initialize services
gainers_service = GainersService()
markets_service = MarketsService()


@app.route('/')
def index():
    return jsonify({
        'name': 'PolyResearch API',
        'version': '1.0.0',
        'endpoints': [
            'GET /api/health',
            'GET /api/gainers',
            'GET /api/markets/watch',
            'GET /api/markets/trending',
            'GET /api/markets/search',
        ]
    })


@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()})


@app.route('/api/gainers')
def get_gainers():
    """
    Get top gainers with filtering options.
    
    Query params:
        hours: Time period in hours (default: 24)
        min_profit: Minimum profit filter (default: 0)
        max_profit: Maximum profit filter (optional)
        min_trades: Minimum trade count (default: 0)
        max_trades: Maximum trade count (optional)
        sort_by: Sort field - profit, trades, activity_gain (default: profit)
        sort_order: asc or desc (default: desc)
        limit: Number of results (default: 20, max: 100)
        offset: Pagination offset (default: 0)
    """
    # Parse filter parameters from request
    filters = {
        'hours': request.args.get('hours', 24, type=int),
        'min_profit': request.args.get('min_profit', 0, type=float),
        'max_profit': request.args.get('max_profit', type=float),
        'min_trades': request.args.get('min_trades', 0, type=int),
        'max_trades': request.args.get('max_trades', type=int),
        'sort_by': request.args.get('sort_by', 'profit'),
        'sort_order': request.args.get('sort_order', 'desc'),
        'limit': min(request.args.get('limit', 20, type=int), 100),
        'offset': request.args.get('offset', 0, type=int),
    }
    
    # Validate hours (1 hour to 30 days)
    filters['hours'] = max(1, min(filters['hours'], 720))
    
    # Get filtered results
    results = gainers_service.find_top_gainers(**filters)
    
    return jsonify({
        'filters': filters,
        'count': len(results),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'results': results
    })


@app.route('/api/markets/watch')
def get_markets_to_watch():
    """
    Get markets worth watching based on scoring algorithm.
    
    Query params:
        limit: Number of results (default: 20)
        min_score: Minimum score threshold (default: 0)
        min_volume: Minimum 24h volume (default: 0)
        min_liquidity: Minimum liquidity (default: 0)
        created_days: Only markets created within N days (optional)
    """
    filters = {
        'limit': min(request.args.get('limit', 20, type=int), 50),
        'min_score': request.args.get('min_score', 0, type=int),
        'min_volume': request.args.get('min_volume', 0, type=float),
        'min_liquidity': request.args.get('min_liquidity', 0, type=float),
        'created_days': request.args.get('created_days', type=int),
    }
    
    results = markets_service.get_markets_to_watch(**filters)
    
    return jsonify({
        'filters': filters,
        'count': len(results),
        'results': results
    })


@app.route('/api/markets/trending')
def get_trending_markets():
    """
    Get trending markets by volume.
    
    Query params:
        period: 24h, 1wk, or 1mo (default: 24h)
        limit: Number of results (default: 20)
        min_volume: Minimum volume threshold (default: 0)
    """
    filters = {
        'period': request.args.get('period', '24h'),
        'limit': min(request.args.get('limit', 20, type=int), 50),
        'min_volume': request.args.get('min_volume', 0, type=float),
    }
    
    # Validate period
    if filters['period'] not in ['24h', '1wk', '1mo']:
        filters['period'] = '24h'
    
    results = markets_service.get_trending_markets(**filters)
    
    return jsonify({
        'filters': filters,
        'count': len(results),
        'results': results
    })


@app.route('/api/markets/search')
def search_markets():
    """
    Search markets by title or slug.
    
    Query params:
        q: Search query (required)
        limit: Number of results (default: 20)
    """
    query = request.args.get('q', '').strip()
    limit = min(request.args.get('limit', 20, type=int), 50)
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    results = markets_service.search_markets(query=query, limit=limit)
    
    return jsonify({
        'query': query,
        'count': len(results),
        'results': results
    })


@app.route('/api/markets/<slug>')
def get_market_details(slug):
    """Get details for a specific market by slug."""
    result = markets_service.get_market_by_slug(slug)
    
    if not result:
        return jsonify({'error': 'Market not found'}), 404
    
    return jsonify(result)


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("Starting PolyResearch API...")
    print("API docs: http://localhost:8000/")
    print("Health check: http://localhost:8000/api/health")
    print("Top gainers: http://localhost:8000/api/gainers")
    app.run(debug=True, host='0.0.0.0', port=8000)
