"""
Markets Service
Market analysis with filtering and scoring
"""

import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from services.polymarket_api import api


class MarketsService:
    """Service for market analysis with filters"""
    
    def get_markets_to_watch(
        self,
        limit: int = 20,
        min_score: int = 0,
        min_volume: float = 0,
        min_liquidity: float = 0,
        created_days: Optional[int] = None
    ) -> List[Dict]:
        """
        Get markets worth watching based on scoring algorithm.
        
        Scoring criteria:
        - Volume growth (24h vs 1wk): +30 points if > 2x
        - Recent creation (< 7 days): +20 points
        - High liquidity (> $10k): +15 points
        - Competitive (30-70% probability): +25 points
        - High volume (> $50k/24h): +10 points
        """
        events = api.get_events(limit=200, active=True)
        
        if not events:
            return []
        
        now = datetime.now(timezone.utc)
        scored = []
        
        for event in events:
            score = 0
            reasons = []
            
            # Get metrics
            volume_24h = float(event.get('volume24hr', 0) or 0)
            volume_1wk = float(event.get('volume1wk', 0) or 0)
            liquidity = float(event.get('liquidity', 0) or 0)
            
            # Apply base filters
            if volume_24h < min_volume:
                continue
            if liquidity < min_liquidity:
                continue
            
            # Parse creation date
            created_at = event.get('createdAt') or event.get('creationDate')
            days_old = None
            if created_at:
                try:
                    created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    days_old = (now - created).days
                    
                    # Filter by creation days if specified
                    if created_days is not None and days_old > created_days:
                        continue
                except:
                    pass
            
            # Scoring: Volume growth
            if volume_1wk > 0:
                growth_ratio = volume_24h / volume_1wk
                if growth_ratio > 2:
                    score += 30
                    reasons.append(f"{growth_ratio:.1f}x volume growth")
            
            # Scoring: Recent creation
            if days_old is not None and days_old <= 7:
                score += 20
                reasons.append(f"Created {days_old} days ago")
            
            # Scoring: High liquidity
            if liquidity > 10000:
                score += 15
                reasons.append(f"High liquidity (${liquidity:,.0f})")
            
            # Scoring: Competitive market
            markets = event.get('markets', [])
            if markets:
                for market in markets[:1]:
                    prices_str = market.get('outcomePrices', '[]')
                    try:
                        if isinstance(prices_str, str):
                            prices = json.loads(prices_str)
                        else:
                            prices = prices_str
                        
                        if prices:
                            max_price = max(float(p) for p in prices)
                            if 0.3 <= max_price <= 0.7:
                                score += 25
                                reasons.append("Competitive market")
                    except:
                        pass
            
            # Scoring: High volume
            if volume_24h > 50000:
                score += 10
                reasons.append(f"High volume (${volume_24h:,.0f})")
            
            # Apply score filter
            if score < min_score:
                continue
            
            scored.append({
                'slug': event.get('slug'),
                'title': event.get('title'),
                'score': score,
                'reasons': reasons,
                'volume_24h': round(volume_24h, 2),
                'volume_1wk': round(volume_1wk, 2),
                'liquidity': round(liquidity, 2),
                'days_old': days_old,
                'url': f"https://polymarket.com/event/{event.get('slug')}"
            })
        
        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        return scored[:limit]
    
    def get_trending_markets(
        self,
        period: str = '24h',
        limit: int = 20,
        min_volume: float = 0
    ) -> List[Dict]:
        """Get trending markets by volume for a given period"""
        events = api.get_events(limit=100, active=True)
        
        if not events:
            return []
        
        volume_key = {
            '24h': 'volume24hr',
            '1wk': 'volume1wk',
            '1mo': 'volume1mo'
        }.get(period, 'volume24hr')
        
        results = []
        for event in events:
            volume = float(event.get(volume_key, 0) or 0)
            
            if volume < min_volume:
                continue
            
            results.append({
                'slug': event.get('slug'),
                'title': event.get('title'),
                'volume': round(volume, 2),
                'volume_24h': round(float(event.get('volume24hr', 0) or 0), 2),
                'liquidity': round(float(event.get('liquidity', 0) or 0), 2),
                'comment_count': event.get('commentCount', 0),
                'url': f"https://polymarket.com/event/{event.get('slug')}"
            })
        
        # Sort by volume descending
        results.sort(key=lambda x: x['volume'], reverse=True)
        
        return results[:limit]
    
    def search_markets(self, query: str, limit: int = 20) -> List[Dict]:
        """Search markets by title or slug"""
        events = api.get_events(limit=200, active=True)
        
        if not events:
            return []
        
        query_lower = query.lower()
        results = []
        
        for event in events:
            title = event.get('title', '').lower()
            slug = event.get('slug', '').lower()
            
            if query_lower in title or query_lower in slug:
                results.append({
                    'slug': event.get('slug'),
                    'title': event.get('title'),
                    'volume_24h': round(float(event.get('volume24hr', 0) or 0), 2),
                    'liquidity': round(float(event.get('liquidity', 0) or 0), 2),
                    'url': f"https://polymarket.com/event/{event.get('slug')}"
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_market_by_slug(self, slug: str) -> Optional[Dict]:
        """Get details for a specific market"""
        event = api.get_event_by_slug(slug)
        
        if not event:
            return None
        
        # Parse markets/outcomes
        markets = event.get('markets', [])
        outcomes = []
        
        for market in markets:
            outcomes_str = market.get('outcomes', '[]')
            prices_str = market.get('outcomePrices', '[]')
            
            try:
                if isinstance(outcomes_str, str):
                    outcome_names = json.loads(outcomes_str)
                else:
                    outcome_names = outcomes_str
                
                if isinstance(prices_str, str):
                    prices = json.loads(prices_str)
                else:
                    prices = prices_str
                
                for i, name in enumerate(outcome_names):
                    price = float(prices[i]) if i < len(prices) else 0
                    outcomes.append({
                        'name': name,
                        'probability': round(price * 100, 1),
                        'group': market.get('groupItemTitle', 'Main')
                    })
            except:
                pass
        
        return {
            'slug': event.get('slug'),
            'title': event.get('title'),
            'description': event.get('description'),
            'volume': round(float(event.get('volume', 0) or 0), 2),
            'volume_24h': round(float(event.get('volume24hr', 0) or 0), 2),
            'liquidity': round(float(event.get('liquidity', 0) or 0), 2),
            'start_date': event.get('startDate'),
            'end_date': event.get('endDate'),
            'active': event.get('active', False),
            'outcomes': outcomes,
            'url': f"https://polymarket.com/event/{event.get('slug')}"
        }
