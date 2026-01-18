from flask import Flask, jsonify, request
from flask_cors import CORS
from find_top_gainers import PolymarketGainTracker
import os
import json
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Gemini client (set GEMINI_API_KEY in environment)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# System prompt for the AI agent
AGENT_SYSTEM_PROMPT = """You are an API parameter extractor for a Polymarket trading analytics API.

Given a user's natural language query, extract the relevant parameters for the /api/traders/top-gainers endpoint.

Available parameters:
- hours: How far back to look (integer, 1-8760). Examples: "last 24 hours" = 24, "past week" = 168, "last month" = 720
- limit: Number of results to return (integer, 1-100). Examples: "top 5" = 5, "top 10" = 10

Return a JSON object with the extracted parameters. Only include parameters that are explicitly or implicitly mentioned.

Examples:
- "Show me the biggest winners today" → {"hours": 24, "limit": 10}
- "Top 5 traders this week" → {"hours": 168, "limit": 5}
- "Who made money in the last 3 days" → {"hours": 72, "limit": 20}
- "Best performing new accounts" → {"hours": 720, "limit": 20}
"""


@app.route('/')
def home():
    return jsonify({"message": "Welcome to the API!"})


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/traders/top-gainers', methods=['GET', 'POST'])
def top_gainers():
    # Support both query params (GET) and JSON body (POST)
    if request.method == 'POST':
        data = request.get_json() or {}
        hours = data.get('hours', 720)
        limit = data.get('limit', 20)
    else:
        hours = request.args.get('hours', default=720, type=int)
        limit = request.args.get('limit', default=20, type=int)

    # Validate inputs
    hours = max(1, min(hours, 8760))  # 1 hour to 1 year
    limit = max(1, min(limit, 100))   # 1 to 100 results
    
    tracker = PolymarketGainTracker()
    results = tracker.find_top_gainers(hours=hours, top_n=limit)
    
    return jsonify({
        "hours": hours,
        "limit": limit,
        "count": len(results),
        "top_gainers": results
    })


@app.route('/api/agent/query', methods=['POST'])
def agent_query():
    """
    Natural language interface for the API.
    
    Example request:
    POST /api/agent/query
    {"query": "Show me top 5 traders who profited in the last 24 hours"}
    
    Returns the extracted parameters + results
    """
    data = request.get_json() or {}
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Call Gemini to extract parameters
        prompt = f"{AGENT_SYSTEM_PROMPT}\n\nUser query: {user_query}\n\nRespond with only valid JSON, no markdown."
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0,
                response_mime_type="application/json"
            )
        )
        
        # Parse the extracted parameters
        extracted = json.loads(response.text)
        
        # Apply defaults and validation
        hours = extracted.get('hours', 720)
        limit = extracted.get('limit', 20)
        hours = max(1, min(int(hours), 8760))
        limit = max(1, min(int(limit), 100))
        
        # Fetch results
        tracker = PolymarketGainTracker()
        results = tracker.find_top_gainers(hours=hours, top_n=limit)
        
        return jsonify({
            "query": user_query,
            "interpreted_as": {
                "hours": hours,
                "limit": limit
            },
            "count": len(results),
            "top_gainers": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)







