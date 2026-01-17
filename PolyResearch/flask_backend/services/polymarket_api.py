"""
Polymarket API Client
Handles all interactions with Polymarket's public APIs
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone


class PolymarketAPI:
    """Client for Polymarket APIs"""
    
    GAMMA_API = "https://gamma-api.polymarket.com"
    DATA_API = "https://data-api.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PolyResearch/1.0'
        })
    
    def get_recent_trades(self, hours: int = 24, limit: int = 2000) -> List[Dict]:
        """Fetch recent trades from Data API"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_ts = int(cutoff.timestamp())
        
        try:
            response = self.session.get(
                f"{self.DATA_API}/trades",
                params={'limit': limit, 'timestamp': cutoff_ts},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching trades: {e}")
            return []
    
    def get_events(self, limit: int = 100, active: bool = True) -> List[Dict]:
        """Fetch events/markets from Gamma API"""
        try:
            response = self.session.get(
                f"{self.GAMMA_API}/events",
                params={
                    'limit': limit,
                    'active': str(active).lower(),
                    'closed': 'false'
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def get_event_by_slug(self, slug: str) -> Optional[Dict]:
        """Fetch a single event by slug"""
        try:
            response = self.session.get(
                f"{self.GAMMA_API}/events/slug/{slug}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
    
    def get_user_activity(self, wallet: str, limit: int = 100) -> List[Dict]:
        """Fetch user activity (may be restricted)"""
        try:
            response = self.session.get(
                f"{self.DATA_API}/activity",
                params={'user': wallet, 'limit': limit},
                timeout=10
            )
            if response.status_code != 200:
                return []
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []


# Global API instance
api = PolymarketAPI()
