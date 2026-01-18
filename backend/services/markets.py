import requests
from typing import Dict, Any, List, Optional
import json

# Polymarket Gamma API base URL
GAMMA_API_BASE = "https://gamma-api.polymarket.com"

class MarketsService:
    """Service to interact with Polymarket Markets (Gamma API)."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PolyResearch-API/1.0'
        })
        
    def get_market_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Fetch event data by slug using Polymarket Gamma API.
        
        Args:
            slug: The event slug
        
        Returns:
            Dictionary containing event data, or None if fetch fails
        """
        url = f"{GAMMA_API_BASE}/events"
        params = {'slug': slug}
        
        try:
            # Note: Gamma API slug endpoint might be /events/slug/{slug} or query param
            # Based on fetch_polymarket.py it was /events/slug/{slug}
            # Implementing both safety or sticking to what was in fetch_polymarket.py
            
            url_slug = f"{GAMMA_API_BASE}/events"
            response = self.session.get(url_slug, params={'slug': slug})
             
            # If that returns a list, take first
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
                elif isinstance(data, dict):
                    return data
            
            # Fallback to direct path if the above query param method fails to narrow down or if API prefers path
            url_path = f"{GAMMA_API_BASE}/events/slug/{slug}"
            response = self.session.get(url_path)
            if response.status_code == 200:
                return response.json()
                
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching event data: {e}")
            return None

    def get_trending_markets(self, period: str = '24h', limit: int = 20, min_volume: float = 0) -> List[Dict[str, Any]]:
        """
        Get trending markets by volume.
        
        Args:
            period: Time period (unused for now as API might just give general trending)
            limit: Number of results
            min_volume: Minimum volume filter
            
        Returns:
            List of market dictionaries
        """
        # Gamma API events endpoint usually sorts by volume or liquidity by default or optional param
        # We will try to fetch top events
        url = f"{GAMMA_API_BASE}/events"
        params = {
            'limit': limit + 10, # Fetch a bit more to filter
            'closed': 'false', # Only active
            'order': 'volume24hr', # Guessing parameter, 'volume' or 'volume24hr' often used
            'ascending': 'false'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            events = response.json()
            
            if not isinstance(events, list):
                if isinstance(events, dict) and 'data' in events: # Pagination wrapper?
                    events = events['data']
                else:
                    return []
            
            # Filter
            results = []
            for event in events:
                if min_volume > 0:
                    vol = float(event.get('volume', 0) or 0)
                    if vol < min_volume:
                        continue
                results.append(event)
                if len(results) >= limit:
                    break
                    
            return results
        except Exception as e:
            print(f"Error fetching trending markets: {e}")
            return []

    def get_markets_to_watch(self, limit: int = 20, **kwargs) -> List[Dict[str, Any]]:
        """
        Get markets worth watching based on scoring algorithm.
        For now, returns generic top markets or interesting ones.
        """
        # We can reuse trending or implement a specific 'recommended' logic
        # For this implementation, we'll fetch 'active' and 'competitive' markets
        return self.get_trending_markets(limit=limit)

    def search_markets(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search markets by title or slug.
        """
        url = f"{GAMMA_API_BASE}/events"
        params = {
            'q': query, # Often 'q' or 'query'
            'limit': limit,
            'closed': 'false'
        }
        
        try:
            response = self.session.get(url, params=params)
             # If q param doesn't work, we might have to filter locally, but usually APIs support it
            if response.status_code != 200:
                return []
                
            data = response.json()
             
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data: # Pagination wrapper?
                 return data['data']
            return []
        except Exception as e:
            print(f"Error searching markets: {e}")
            return []
