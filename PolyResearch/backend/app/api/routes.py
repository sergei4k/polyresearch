"""
API Routes
"""

from fastapi import APIRouter, Query
from datetime import datetime, timezone
from typing import Optional

from app.models.schemas import (
    TopGainersResponse, TopGainer,
    MarketsToWatchResponse, MarketToWatch,
    TrendingMarketsResponse, TrendingMarket,
    VolumeLeadersResponse, VolumeLeader
)
from app.services.top_gainers import service as gainers_service
from app.services.markets import service as markets_service
from app.api.polymarket import client

router = APIRouter()


@router.get("/top-gainers", response_model=TopGainersResponse)
async def get_top_gainers(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    top_n: int = Query(20, ge=1, le=100, description="Number of top gainers")
):
    """Get top gainers among new accounts"""
    gainers = gainers_service.find_top_gainers(hours=hours, top_n=top_n)
    
    return TopGainersResponse(
        gainers=[TopGainer(**g) for g in gainers],
        period_hours=hours,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/markets/watch", response_model=MarketsToWatchResponse)
async def get_markets_to_watch(
    limit: int = Query(20, ge=1, le=50, description="Number of markets to return")
):
    """Get markets worth watching"""
    markets = markets_service.get_markets_to_watch(limit=limit)
    
    return MarketsToWatchResponse(
        markets=[MarketToWatch(**m) for m in markets]
    )


@router.get("/markets/trending", response_model=TrendingMarketsResponse)
async def get_trending_markets(
    limit: int = Query(20, ge=1, le=50, description="Number of markets to return")
):
    """Get trending markets by volume"""
    markets = markets_service.get_trending_markets(limit=limit)
    
    return TrendingMarketsResponse(
        markets=[TrendingMarket(**m) for m in markets]
    )


@router.get("/markets/volume-leaders", response_model=VolumeLeadersResponse)
async def get_volume_leaders(
    period: str = Query("24h", regex="^(24h|1wk|1mo)$", description="Time period"),
    limit: int = Query(20, ge=1, le=50, description="Number of markets to return")
):
    """Get markets with highest volume"""
    markets = markets_service.get_volume_leaders(period=period, limit=limit)
    
    return VolumeLeadersResponse(
        markets=[VolumeLeader(**m) for m in markets],
        period=period
    )


@router.get("/markets/{slug}")
async def get_market_details(slug: str):
    """Get details for a specific market/event"""
    event = client.get_event_by_slug(slug)
    
    if not event:
        return {"error": "Market not found"}
    
    return event


@router.get("/markets/search")
async def search_markets(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=50)
):
    """Search markets by title or slug"""
    results = client.search_events(q, limit=limit)
    return {"query": q, "results": results, "count": len(results)}
