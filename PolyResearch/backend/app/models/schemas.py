"""
Pydantic models for API requests/responses
"""

from pydantic import BaseModel
from typing import List, Optional


class TopGainer(BaseModel):
    wallet: str
    gain: float
    trade_count: int


class TopGainersResponse(BaseModel):
    gainers: List[TopGainer]
    period_hours: int
    timestamp: str


class MarketToWatch(BaseModel):
    slug: str
    title: str
    score: int
    reasons: List[str]
    volume24hr: float
    volume1wk: float
    liquidity: float
    createdAt: Optional[str] = None


class MarketsToWatchResponse(BaseModel):
    markets: List[MarketToWatch]


class TrendingMarket(BaseModel):
    slug: str
    title: str
    volume24hr: float
    volume1wk: float
    liquidity: float
    commentCount: int
    competitive: float


class TrendingMarketsResponse(BaseModel):
    markets: List[TrendingMarket]


class VolumeLeader(BaseModel):
    slug: str
    title: str
    volume: float
    liquidity: float


class VolumeLeadersResponse(BaseModel):
    markets: List[VolumeLeader]
    period: str
