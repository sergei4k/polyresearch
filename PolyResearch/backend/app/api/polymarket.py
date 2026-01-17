"""
Polymarket API Client
Handles all interactions with Polymarket's public APIs
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone


class PolymarketClient:
    """Client for Polymarket APIs"""
    
    GAMMA_API_BASE = "https://gamma-api.polymarket.com"
    DATA_API_BASE = "https://data-api.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PolyResearch/1.0'
        })
    
    def get_event_by_slug(self, slug: str) -> Optional[Dict]:
        """Get event data by slug"""
        url = f"{self.GAMMA_API_BASE}/events/slug/{slug}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
        """Get event data by ID"""
        url = f"{self.GAMMA_API_BASE}/events/{event_id}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def list_events(self, limit: int = 100, active: bool = True, 
                   closed: bool = False, sort_by: str = "volume") -> List[Dict]:
        """List events/markets"""
        url = f"{self.GAMMA_API_BASE}/events"
        params = {
            'limit': limit,
            'active': str(active).lower(),
            'closed': str(closed).lower(),
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            return []
        except requests.exceptions.RequestException:
            return []
    
    def get_recent_trades(self, hours: int = 24, limit: int = 1000) -> List[Dict]:
        """Get recent trades"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        url = f"{self.DATA_API_BASE}/trades"
        params = {
            'limit': limit,
            'timestamp': cutoff_timestamp,
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            return []
        except requests.exceptions.RequestException:
            return []
    
    def search_events(self, query: str, limit: int = 50) -> List[Dict]:
        """Search events by title/slug"""
        events = self.list_events(limit=200)  # Get more to search through
        
        query_lower = query.lower()
        results = []
        
        for event in events:
            title = event.get('title', '').lower()
            slug = event.get('slug', '').lower()
            
            if query_lower in title or query_lower in slug:
                results.append(event)
                if len(results) >= limit:
                    break
        
        return results


# Global client instance
client = PolymarketClient()
