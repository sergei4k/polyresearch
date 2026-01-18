import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import time

# Polymarket API endpoints
DATA_API_BASE = "https://data-api.polymarket.com"

class GainersService:
    """Track gains for new accounts on Polymarket."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Polymarket-Gain-Tracker/1.0'
        })
    
    def get_recent_trades(self, hours: int = 720, limit: int = 1000) -> List[Dict]:
        """
        Fetch recent trades from Polymarket.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of trades to fetch
        
        Returns:
            List of trade dictionaries
        """
        # Calculate timestamp cutoff
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        url = f"{DATA_API_BASE}/trades"
        params = {
            'limit': limit,
            'timestamp': cutoff_timestamp,
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            elif isinstance(data, dict) and 'trades' in data:
                return data['trades']
            else:
                print(f"Warning: Unexpected response format: {type(data)}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trades: {e}")
            return []
    
    def get_user_activity(self, user: str, limit: int = 100) -> List[Dict]:
        """
        Get activity for a specific user.
        
        Note: The activity endpoint may have restrictions or require authentication.
        This method attempts to fetch activity but may return empty if unavailable.
        
        Args:
            user: Wallet address or proxy wallet
            limit: Maximum number of activities to fetch
        
        Returns:
            List of activity dictionaries
        """
        url = f"{DATA_API_BASE}/activity"
        params = {
            'user': user,
            'limit': limit,
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            # Don't raise for status - may not be available for all users
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            elif isinstance(data, dict) and 'activities' in data:
                return data['activities']
            return []
        except requests.exceptions.RequestException:
            # Some users may not have accessible activity or endpoint may be restricted
            return []
    
    def is_new_account(self, wallet: str, cutoff_time: datetime, trades: List[Dict]) -> bool:
        """
        Check if an account is "new" by examining their first trade.
        
        Since activity endpoint may be restricted, we use trades data instead.
        An account is considered "new" if their earliest trade is after the cutoff time.
        
        Args:
            wallet: Wallet address to check
            cutoff_time: Time cutoff (e.g., 30 days ago)
            trades: List of all trades to search through
        
        Returns:
            True if account appears to be new (first trade within cutoff)
        """
        # Get all trades for this wallet
        wallet_trades = [t for t in trades if (t.get('proxyWallet') == wallet or t.get('user') == wallet)]
        
        if not wallet_trades:
            return False
        
        # Find the earliest trade for this wallet
        earliest_trade = None
        earliest_timestamp = None
        
        for trade in wallet_trades:
            timestamp = trade.get('timestamp')
            if timestamp:
                try:
                    if isinstance(timestamp, (int, float)):
                        trade_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    elif isinstance(timestamp, str):
                        trade_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        continue
                    
                    if earliest_timestamp is None or trade_time < earliest_timestamp:
                        earliest_timestamp = trade_time
                        earliest_trade = trade
                except:
                    continue
        
        if earliest_timestamp is None:
            return False
        
        # Account is "new" if earliest trade is after cutoff
        return earliest_timestamp >= cutoff_time
    
    def calculate_gain_from_trades(self, wallet: str, trades: List[Dict]) -> float:
        """
        Calculate approximate gain from a user's trades.
        
        This is a simplified calculation:
        - Realized gains: SELL proceeds - BUY costs
        - This doesn't account for unrealized positions or market resolution
        
        Args:
            wallet: Wallet address
            trades: List of trades for this wallet
        
        Returns:
            Estimated gain in USD
        """
        user_trades = [t for t in trades if t.get('proxyWallet') == wallet or t.get('user') == wallet]
        
        if not user_trades:
            return 0.0
        
        total_cost = 0.0
        total_proceeds = 0.0
        
        for trade in user_trades:
            side = trade.get('side', '').upper()
            price = float(trade.get('price', 0))
            size = float(trade.get('size', 0) or trade.get('usdcSize', 0))
            
            if side == 'BUY':
                total_cost += price * size
            elif side == 'SELL':
                total_proceeds += price * size
        
        # Gain = proceeds - cost
        gain = total_proceeds - total_cost
        return gain
    
    def calculate_gain_from_activity(self, wallet: str, activities: List[Dict]) -> float:
        """
        Calculate gain from user activity (redeems, trades, etc.).
        
        Args:
            wallet: Wallet address
            activities: List of activities for this wallet
        
        Returns:
            Estimated gain in USD
        """
        total_gain = 0.0
        
        for activity in activities:
            activity_type = activity.get('type', '').upper()
            
            # REDEEM activities represent realized gains from winning positions
            if activity_type == 'REDEEM':
                usdc_size = float(activity.get('usdcSize', 0) or activity.get('amount', 0))
                total_gain += usdc_size
            
            # TRADE activities - simplified calculation
            elif activity_type == 'TRADE':
                side = activity.get('side', '').upper()
                usdc_size = float(activity.get('usdcSize', 0) or activity.get('amount', 0))
                
                if side == 'BUY':
                    total_gain -= usdc_size  # Cost
                elif side == 'SELL':
                    total_gain += usdc_size  # Proceeds
        
        return total_gain
    
    def find_top_gainers(self, hours: int = 24, limit: int = 20, min_profit: float = 0, sort_by: str = 'profit', **kwargs) -> List[Dict]:
        """
        Find top gainers among new accounts in the last N hours.
        
        Args:
            hours: Number of hours to look back
            limit: Number of top gainers to return
            min_profit: Minimum profit filter
            sort_by: Field to sort by
        
        Returns:
            List of dictionaries with wallet, gain, and metadata
        """
        print(f"🔍 Analyzing Polymarket activity for the last {hours} hours...")
        
        # Get cutoff time
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Step 1: Fetch recent trades
        # Note: We fetch more trades than limit usually to ensure we catch enough activity
        fetch_limit = 2000
        if hours > 24:
            fetch_limit = 5000
            
        print("📊 Fetching recent trades...")
        trades = self.get_recent_trades(hours=hours, limit=fetch_limit)
        print(f"   Found {len(trades)} trades")
        
        if not trades:
            return []
        
        # Step 2: Extract unique wallets
        wallets = set()
        for trade in trades:
            wallet = trade.get('proxyWallet') or trade.get('user') or trade.get('wallet')
            if wallet:
                wallets.add(wallet)
        
        print(f"   Found {len(wallets)} unique wallets")
        
        # Step 3: Filter for new accounts
        print("🆕 Identifying new accounts...")
        new_wallets = []
        checked = 0
        
        for wallet in wallets:
            checked += 1
            if self.is_new_account(wallet, cutoff_time, trades):
                new_wallets.append(wallet)
        
        print(f"\n   Found {len(new_wallets)} new accounts")
        
        if not new_wallets:
            return []
        
        # Step 4: Calculate gains for new accounts
        print("💰 Calculating gains for new accounts...")
        gains_data = []
        
        for i, wallet in enumerate(new_wallets):
            # Calculate gain from trades
            trade_gain = self.calculate_gain_from_trades(wallet, trades)

            if trade_gain >= min_profit:
                gains_data.append({
                    'wallet': wallet,
                    'profit': trade_gain,
                    'gain': trade_gain,
                    'trade_gain': trade_gain,
                    'activity_gain': 0,
                    'trades': len([t for t in trades if t.get('proxyWallet') == wallet or t.get('user') == wallet]),
                    'activity_count': 0
                })
        
        # Step 5: Sort
        if sort_by == 'activity_gain':
            gains_data.sort(key=lambda x: x['activity_gain'], reverse=True)
        elif sort_by == 'trades':
            gains_data.sort(key=lambda x: x['trades'], reverse=True)
        else:
            gains_data.sort(key=lambda x: x['profit'], reverse=True)
            
        return gains_data[:limit]
