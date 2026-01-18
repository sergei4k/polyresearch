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

    def get_markets_by_category(self, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch markets by category/tag.

        Args:
            category: Market category (e.g., 'Trending', 'Politics', 'Sports', 'Crypto')
            limit: Maximum number of markets to return

        Returns:
            List of market dictionaries with their token IDs
        """
        url = f"{GAMMA_API_BASE}/events"

        # Map frontend category names to API tags (lowercase for API)
        # Polymarket API often uses lowercase tags
        category_tag = category.lower().replace(' & ', '-').replace(' ', '-')

        params = {
            'limit': limit,
            'closed': 'false',
            'tag': category_tag if category != 'Trending' else None,
            'order': 'volume24hr',
            'ascending': 'false'
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            events = response.json()

            if not isinstance(events, list):
                if isinstance(events, dict) and 'data' in events:
                    events = events['data']
                else:
                    return []

            # Extract token IDs from markets within events
            markets_with_tokens = []
            for event in events:
                event_markets = event.get('markets', [])
                for market in event_markets:
                    markets_with_tokens.append({
                        'event_id': event.get('id'),
                        'event_slug': event.get('slug'),
                        'market_id': market.get('id'),
                        'token_id': market.get('clobTokenIds', []),  # This is often an array
                        'condition_id': market.get('conditionId'),
                        'question': market.get('question'),
                    })

            return markets_with_tokens
        except Exception as e:
            print(f"Error fetching markets by category '{category}': {e}")
            return []

    def get_token_ids_for_category(self, category: str) -> set:
        """
        Get all token IDs for markets in a given category.

        Args:
            category: Market category

        Returns:
            Set of token IDs (as strings)
        """
        markets = self.get_markets_by_category(category, limit=200)
        token_ids = set()

        for market in markets:
            token_id_list = market.get('token_id', [])
            if isinstance(token_id_list, list):
                # token_id_list contains individual token IDs as strings
                for token_id in token_id_list:
                    if isinstance(token_id, str):
                        token_ids.add(token_id)
                    elif isinstance(token_id, list):
                        # If it's a nested list, flatten it
                        token_ids.update(str(tid) for tid in token_id)
            elif isinstance(token_id_list, str):
                # If it's a JSON string like '["123", "456"]', parse it
                try:
                    parsed = json.loads(token_id_list)
                    if isinstance(parsed, list):
                        token_ids.update(str(tid) for tid in parsed)
                    else:
                        token_ids.add(token_id_list)
                except:
                    # Not JSON, just add as-is
                    token_ids.add(token_id_list)
            elif token_id_list:  # Single value
                token_ids.add(str(token_id_list))

        return token_ids
