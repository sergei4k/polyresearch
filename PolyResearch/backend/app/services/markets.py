"""
Markets Service
Analyzes and ranks markets for insights
"""

from typing import List, Dict
from datetime import datetime, timedelta, timezone
from app.api.polymarket import client


class MarketsService:
    """Service for market analysis"""
    
    def get_markets_to_watch(self, limit: int = 20) -> List[Dict]:
        """
        Get markets worth watching based on multiple criteria
        
        Criteria:
        - High volume growth (24h vs 1wk)
        - Recent creation (last 7 days)
        - High liquidity
        - Price movement
        - Competitive (uncertain outcomes)
        """
        events = client.list_events(limit=200, active=True, closed=False)
        
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        
        scored_markets = []
        
        for event in events:
            score = 0
            reasons = []
            
            # Check volume growth
            volume_24h = float(event.get('volume24hr', 0) or 0)
            volume_1wk = float(event.get('volume1wk', 0) or 0)
            
            if volume_1wk > 0:
                growth_ratio = volume_24h / volume_1wk
                if growth_ratio > 2:
                    score += 30
                    reasons.append(f"{growth_ratio:.1f}x volume growth")
            
            # Check if recently created
            created_at = event.get('createdAt') or event.get('creationDate')
            if created_at:
                try:
                    created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    days_old = (now - created).days
                    if days_old <= 7:
                        score += 20
                        reasons.append(f"Created {days_old} days ago")
                except:
                    pass
            
            # Check liquidity
            liquidity = float(event.get('liquidity', 0) or 0)
            if liquidity > 10000:
                score += 15
                reasons.append(f"High liquidity (${liquidity:,.0f})")
            
            # Check competitive status (close probabilities)
            markets = event.get('markets', [])
            if markets:
                for market in markets[:1]:  # Check first market
                    prices_str = market.get('outcomePrices', '[]')
                    if isinstance(prices_str, str):
                        import json
                        try:
                            prices = json.loads(prices_str)
                            if prices:
                                max_price = max(float(p) for p in prices)
                                min_price = min(float(p) for p in prices)
                                if 0.3 <= max_price <= 0.7:  # Competitive range
                                    score += 25
                                    reasons.append("Competitive market")
                        except:
                            pass
            
            # High 24h volume
            if volume_24h > 50000:
                score += 10
                reasons.append(f"High volume (${volume_24h:,.0f})")
            
            if score > 0:
                scored_markets.append({
                    'slug': event.get('slug'),
                    'title': event.get('title'),
                    'score': score,
                    'reasons': reasons,
                    'volume24hr': volume_24h,
                    'volume1wk': volume_1wk,
                    'liquidity': liquidity,
                    'createdAt': created_at,
                })
        
        # Sort by score
        scored_markets.sort(key=lambda x: x['score'], reverse=True)
        return scored_markets[:limit]
    
    def get_trending_markets(self, limit: int = 20) -> List[Dict]:
        """Get trending markets by volume and activity"""
        events = client.list_events(limit=100, active=True, closed=False)
        
        # Sort by 24h volume
        sorted_events = sorted(
            events,
            key=lambda x: float(x.get('volume24hr', 0) or 0),
            reverse=True
        )
        
        trending = []
        for event in sorted_events[:limit]:
            trending.append({
                'slug': event.get('slug'),
                'title': event.get('title'),
                'volume24hr': float(event.get('volume24hr', 0) or 0),
                'volume1wk': float(event.get('volume1wk', 0) or 0),
                'liquidity': float(event.get('liquidity', 0) or 0),
                'commentCount': event.get('commentCount', 0),
                'competitive': event.get('competitive', 0),
            })
        
        return trending
    
    def get_volume_leaders(self, period: str = '24h', limit: int = 20) -> List[Dict]:
        """Get markets with highest volume"""
        events = client.list_events(limit=100, active=True, closed=False)
        
        volume_key = {
            '24h': 'volume24hr',
            '1wk': 'volume1wk',
            '1mo': 'volume1mo'
        }.get(period, 'volume24hr')
        
        sorted_events = sorted(
            events,
            key=lambda x: float(x.get(volume_key, 0) or 0),
            reverse=True
        )
        
        leaders = []
        for event in sorted_events[:limit]:
            leaders.append({
                'slug': event.get('slug'),
                'title': event.get('title'),
                'volume': float(event.get(volume_key, 0) or 0),
                'liquidity': float(event.get('liquidity', 0) or 0),
            })
        
        return leaders


# Global service instance
service = MarketsService()
