"""
Top Gainers Service
Identifies accounts with largest gains among new accounts
"""

from typing import List, Dict
from datetime import datetime, timedelta, timezone
from app.api.polymarket import client


class TopGainersService:
    """Service for calculating top gainers"""
    
    def find_top_gainers(self, hours: int = 24, top_n: int = 20) -> List[Dict]:
        """
        Find top gainers among new accounts
        
        Args:
            hours: Number of hours to look back
            top_n: Number of top gainers to return
        
        Returns:
            List of gainer dictionaries
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        # Get recent trades
        trades = client.get_recent_trades(hours=hours, limit=2000)
        
        if not trades:
            return []
        
        # Extract unique wallets
        wallets = set()
        for trade in trades:
            wallet = trade.get('proxyWallet') or trade.get('user') or trade.get('wallet')
            if wallet:
                wallets.add(wallet)
        
        # Filter for new accounts (first trade in window)
        new_wallets = []
        for wallet in wallets:
            if self._is_new_account(wallet, cutoff_time, trades):
                new_wallets.append(wallet)
        
        # Calculate gains
        gains_data = []
        for wallet in new_wallets:
            gain = self._calculate_gain(wallet, trades)
            if gain > 0:
                trade_count = len([t for t in trades if 
                                 t.get('proxyWallet') == wallet or 
                                 t.get('user') == wallet])
                
                gains_data.append({
                    'wallet': wallet,
                    'gain': round(gain, 2),
                    'trade_count': trade_count
                })
        
        # Sort and return top N
        gains_data.sort(key=lambda x: x['gain'], reverse=True)
        return gains_data[:top_n]
    
    def _is_new_account(self, wallet: str, cutoff_time: datetime, trades: List[Dict]) -> bool:
        """Check if account is new (first trade within cutoff)"""
        wallet_trades = [t for t in trades if 
                        (t.get('proxyWallet') == wallet or t.get('user') == wallet)]
        
        if not wallet_trades:
            return False
        
        earliest_timestamp = None
        for trade in wallet_trades:
            timestamp = trade.get('timestamp')
            if timestamp:
                try:
                    if isinstance(timestamp, (int, float)):
                        trade_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    else:
                        continue
                    
                    if earliest_timestamp is None or trade_time < earliest_timestamp:
                        earliest_timestamp = trade_time
                except:
                    continue
        
        return earliest_timestamp and earliest_timestamp >= cutoff_time
    
    def _calculate_gain(self, wallet: str, trades: List[Dict]) -> float:
        """Calculate gain from trades"""
        user_trades = [t for t in trades if 
                      t.get('proxyWallet') == wallet or t.get('user') == wallet]
        
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
        
        return total_proceeds - total_cost


# Global service instance
service = TopGainersService()
