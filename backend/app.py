"""
PolyResearch API
Polymarket analytics with AI-powered natural language queries
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import os
import json
import google.generativeai as genai

from services.gainers import GainersService
from services.markets import MarketsService

app = Flask(__name__)
CORS(app)

# Initialize services
gainers_service = GainersService()
markets_service = MarketsService()

# Initialize Gemini (optional - only if API key is set)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None

# AI Agent system prompt
AGENT_SYSTEM_PROMPT = """You are an API parameter extractor for a Polymarket analytics API.

Extract parameters from natural language queries. Return a JSON object with:

For /api/gainers endpoint:
- hours: Time period (integer, 1-720). "today"=24, "this week"=168, "this month"=720
- limit: Number of results (integer, 1-100)
- min_profit: Minimum profit in USD (float)
- sort_by: "profit", "trades", or "activity_gain"

For /api/markets endpoints:
- endpoint: "watch", "trending", or "search"
- limit: Number of results
- period: "24h", "1wk", "1mo" (for trending)
- query: Search term (for search)

Examples:
- "top 5 gainers today" → {"endpoint": "gainers", "hours": 24, "limit": 5}
- "trending markets this week" → {"endpoint": "trending", "period": "1wk"}
- "search bitcoin markets" → {"endpoint": "search", "query": "bitcoin"}
- "who made over $1000 in the last 3 days" → {"endpoint": "gainers", "hours": 72, "min_profit": 1000}
"""


# ============== Core Routes ==============

@app.route('/')
def index():
    return jsonify({
        'name': 'PolyResearch API',
        'version': '2.0.0',
        'endpoints': {
            'health': 'GET /health',
            'gainers': 'GET /api/gainers?hours=24&limit=20&min_profit=0&sort_by=profit',
            'markets_watch': 'GET /api/markets/watch?limit=20',
            'markets_trending': 'GET /api/markets/trending?period=24h',
            'markets_search': 'GET /api/markets/search?q=query',
            'market_detail': 'GET /api/markets/<slug>',
            'ai_query': 'POST /api/agent/query {"query": "your question"}'
        }
    })


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'gemini_enabled': gemini_model is not None
    })


# ============== Gainers Routes ==============

@app.route('/api/gainers', methods=['GET', 'POST'])
def get_gainers():
    """
    Get top gainers with filtering.
    
    Query params:
        hours: Time period (default: 24, max: 720)
        limit: Number of results (default: 20, max: 100)
        min_profit: Minimum profit filter (default: 0)
        max_profit: Maximum profit filter (optional)
        min_trades: Minimum trade count (default: 0)
        max_trades: Maximum trade count (optional)
        sort_by: profit, trades, activity_gain (default: profit)
        sort_order: asc or desc (default: desc)
        offset: Pagination offset (default: 0)
    """
    if request.method == 'POST':
        data = request.get_json() or {}
        filters = {
            'hours': data.get('hours', 24),
            'limit': min(data.get('limit', 20), 100),
            'min_profit': data.get('min_profit', 0),
            'max_profit': data.get('max_profit'),
            'min_trades': data.get('min_trades', 0),
            'max_trades': data.get('max_trades'),
            'sort_by': data.get('sort_by', 'profit'),
            'sort_order': data.get('sort_order', 'desc'),
            'offset': data.get('offset', 0),
        }
    else:
        filters = {
            'hours': request.args.get('hours', 24, type=int),
            'limit': min(request.args.get('limit', 20, type=int), 100),
            'min_profit': request.args.get('min_profit', 0, type=float),
            'max_profit': request.args.get('max_profit', type=float),
            'min_trades': request.args.get('min_trades', 0, type=int),
            'max_trades': request.args.get('max_trades', type=int),
            'sort_by': request.args.get('sort_by', 'profit'),
            'sort_order': request.args.get('sort_order', 'desc'),
            'offset': request.args.get('offset', 0, type=int),
        }
    
    # Validate hours
    filters['hours'] = max(1, min(filters['hours'], 720))
    
    results = gainers_service.find_top_gainers(**filters)
    
    return jsonify({
        'filters': filters,
        'count': len(results),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'results': results
    })


# ============== Markets Routes ==============

@app.route('/api/markets/watch')
def get_markets_to_watch():
    """Get markets worth watching based on scoring algorithm."""
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
    """Get trending markets by volume."""
    filters = {
        'period': request.args.get('period', '24h'),
        'limit': min(request.args.get('limit', 20, type=int), 50),
        'min_volume': request.args.get('min_volume', 0, type=float),
    }
    
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
    """Search markets by title or slug."""
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


# ============== AI Agent Route ==============

@app.route('/api/agent/query', methods=['POST'])
def agent_query():
    """
    Natural language interface for the API.
    
    POST /api/agent/query
    {"query": "Show me top 5 traders who profited in the last 24 hours"}
    """
    if not gemini_model:
        return jsonify({'error': 'Gemini API key not configured. Set GEMINI_API_KEY environment variable.'}), 503
    
    data = request.get_json() or {}
    user_query = data.get('query', '').strip()
    
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Extract parameters using Gemini
        prompt = f"{AGENT_SYSTEM_PROMPT}\n\nUser query: {user_query}\n\nRespond with only valid JSON."
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0,
                response_mime_type="application/json"
            )
        )
        
        extracted = json.loads(response.text)
        endpoint = extracted.get('endpoint', 'gainers')
        
        # Route to appropriate service
        if endpoint == 'gainers':
            hours = max(1, min(int(extracted.get('hours', 24)), 720))
            limit = max(1, min(int(extracted.get('limit', 20)), 100))
            min_profit = float(extracted.get('min_profit', 0))
            sort_by = extracted.get('sort_by', 'profit')
            
            results = gainers_service.find_top_gainers(
                hours=hours, limit=limit, min_profit=min_profit, sort_by=sort_by
            )
            
            return jsonify({
                'query': user_query,
                'interpreted_as': {'endpoint': 'gainers', 'hours': hours, 'limit': limit, 'min_profit': min_profit},
                'count': len(results),
                'results': results
            })
        
        elif endpoint == 'trending':
            period = extracted.get('period', '24h')
            limit = max(1, min(int(extracted.get('limit', 20)), 50))
            
            results = markets_service.get_trending_markets(period=period, limit=limit)
            
            return jsonify({
                'query': user_query,
                'interpreted_as': {'endpoint': 'trending', 'period': period, 'limit': limit},
                'count': len(results),
                'results': results
            })
        
        elif endpoint == 'search':
            search_query = extracted.get('query', '')
            limit = max(1, min(int(extracted.get('limit', 20)), 50))
            
            results = markets_service.search_markets(query=search_query, limit=limit)
            
            return jsonify({
                'query': user_query,
                'interpreted_as': {'endpoint': 'search', 'search_query': search_query, 'limit': limit},
                'count': len(results),
                'results': results
            })
        
        elif endpoint == 'watch':
            limit = max(1, min(int(extracted.get('limit', 20)), 50))
            
            results = markets_service.get_markets_to_watch(limit=limit)
            
            return jsonify({
                'query': user_query,
                'interpreted_as': {'endpoint': 'watch', 'limit': limit},
                'count': len(results),
                'results': results
            })
        
        else:
            return jsonify({'error': f'Unknown endpoint: {endpoint}'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============== Error Handlers ==============

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n🚀 PolyResearch API Starting...")
    print("=" * 50)
    print(f"📍 URL: http://localhost:5000")
    print(f"❤️  Health: http://localhost:5000/health")
    print(f"📈 Gainers: http://localhost:5000/api/gainers")
    print(f"🔥 Trending: http://localhost:5000/api/markets/trending")
    print(f"🤖 AI Agent: POST http://localhost:5000/api/agent/query")
    print("=" * 50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
