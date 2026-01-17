import httpx
from typing import Any


class PolymarketClient:
    """Client for interacting with Polymarket APIs."""
    
    def __init__(self, clob_base_url: str, gamma_base_url: str):
        self.clob_base_url = clob_base_url
        self.gamma_base_url = gamma_base_url
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    # =========================================================================
    # CLOB API Methods
    # =========================================================================
    
    async def get_markets(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Fetch markets from the CLOB API."""
        client = await self._get_client()
        response = await client.get(
            f"{self.clob_base_url}/markets",
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()
    
    async def get_market(self, condition_id: str) -> dict[str, Any]:
        """Fetch a single market by condition ID."""
        client = await self._get_client()
        response = await client.get(f"{self.clob_base_url}/markets/{condition_id}")
        response.raise_for_status()
        return response.json()
    
    async def get_trades(
        self, 
        market_id: str | None = None,
        maker: str | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch trade history."""
        client = await self._get_client()
        params = {"limit": limit}
        if market_id:
            params["market"] = market_id
        if maker:
            params["maker"] = maker
        
        response = await client.get(f"{self.clob_base_url}/trades", params=params)
        response.raise_for_status()
        return response.json()
    
    # =========================================================================
    # Gamma API Methods (for richer market data)
    # =========================================================================
    
    async def get_gamma_markets(
        self,
        limit: int = 100,
        active: bool = True,
        closed: bool = False
    ) -> list[dict[str, Any]]:
        """Fetch markets from Gamma API with additional metadata."""
        client = await self._get_client()
        params = {
            "limit": limit,
            "active": str(active).lower(),
            "closed": str(closed).lower()
        }
        response = await client.get(f"{self.gamma_base_url}/markets", params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_gamma_events(self, limit: int = 100) -> list[dict[str, Any]]:
        """Fetch events (groups of related markets)."""
        client = await self._get_client()
        response = await client.get(
            f"{self.gamma_base_url}/events",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    # =========================================================================
    # Placeholder methods - expand based on actual API exploration
    # =========================================================================
    
    async def get_orderbook(self, token_id: str) -> dict[str, Any]:
        """Fetch orderbook for a specific token."""
        client = await self._get_client()
        response = await client.get(f"{self.clob_base_url}/book", params={"token_id": token_id})
        response.raise_for_status()
        return response.json()
    
    async def get_prices_history(
        self, 
        token_id: str,
        interval: str = "1d",
        fidelity: int = 60
    ) -> list[dict[str, Any]]:
        """Fetch price history for a token."""
        client = await self._get_client()
        response = await client.get(
            f"{self.clob_base_url}/prices-history",
            params={
                "market": token_id,
                "interval": interval,
                "fidelity": fidelity
            }
        )
        response.raise_for_status()
        return response.json()