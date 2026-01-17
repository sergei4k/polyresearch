"""
Gainers Service
Find top gainers among accounts with filtering support
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from services.polymarket_api import api


class GainersService:
    """Service for finding top gainers with filters"""
    
    def find_top_gainers(
        self,
        hours: int = 24,
        min_profit: float = 0,
        max_profit: Optional[float] = None,
        min_trades: int = 0,
        max_trades: Optional[int] = None,
        sort_by: str = 'profit',
        sort_order: str = 'desc',
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """
        Find top gainers with comprehensive filtering.
        
        Args:
            hours: Time period to analyze
            min_profit: Minimum profit threshold
            max_profit: Maximum profit threshold
            min_trades: Minimum trade count
            max_trades: Maximum trade count
            sort_by: Field to sort by (profit, trades, activity_gain)
            sort_order: Sort direction (asc, desc)
            limit: Number of results to return
            offset: Pagination offset
        
        Returns:
            List of account dictionaries with metrics
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # 1. Fetch trades for the period
        trades = api.get_recent_trades(hours=hours, limit=2000)
        
        if not trades:
            return []
        
        # 2. Aggregate trades by wallet
        accounts = self._aggregate_by_wallet(trades, cutoff_time)
        
        # 3. Apply filters
        filtered = self._apply_filters(
            accounts,
            min_profit=min_profit,
            max_profit=max_profit,
            min_trades=min_trades,
            max_trades=max_trades
        )
        
        # 4. Sort results
        filtered = self._sort_results(filtered, sort_by, sort_order)
        
        # 5. Apply pagination
        return filtered[offset:offset + limit]
    
    def _aggregate_by_wallet(self, trades: List[Dict], cutoff_time: datetime) -> List[Dict]:
        """Aggregate trades by wallet and calculate metrics"""
        wallet_data = {}
        
        for trade in trades:
            wallet = trade.get('proxyWallet') or trade.get('user')
            if not wallet:
                continue
            
            if wallet not in wallet_data:
                wallet_data[wallet] = {
                    'wallet': wallet,
                    'buys': 0,
                    'sells': 0,
                    'buy_volume': 0,
                    'sell_volume': 0,
                    'trades': [],
                    'markets': set(),
                    'earliest_trade': None
                }
            
            data = wallet_data[wallet]
            
            side = trade.get('side', '').upper()
            price = float(trade.get('price', 0))
            size = float(trade.get('size', 0) or trade.get('usdcSize', 0))
            value = price * size
            
            if side == 'BUY':
                data['buys'] += 1
                data['buy_volume'] += value
            elif side == 'SELL':
                data['sells'] += 1
                data['sell_volume'] += value
            
            data['trades'].append(trade)
            
            market = trade.get('slug') or trade.get('market')
            if market:
                data['markets'].add(market)
            
            # Track earliest trade
            timestamp = trade.get('timestamp')
            if timestamp:
                try:
                    trade_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    if data['earliest_trade'] is None or trade_time < data['earliest_trade']:
                        data['earliest_trade'] = trade_time
                except:
                    pass
        
        # Calculate final metrics
        results = []
        for wallet, data in wallet_data.items():
            profit = data['sell_volume'] - data['buy_volume']
            trade_count = data['buys'] + data['sells']
            
            # Determine if "new" account (first trade within period)
            is_new = data['earliest_trade'] and data['earliest_trade'] >= cutoff_time
            
            # Get activity gain (from user activity endpoint if available)
            activity_gain = self._get_activity_gain(wallet, data['trades'])
            
            # Use higher of trade profit or activity gain
            total_gain = max(profit, activity_gain)
            
            results.append({
                'wallet': wallet,
                'profit': round(profit, 2),
                'activity_gain': round(activity_gain, 2),
                'total_gain': round(total_gain, 2),
                'trade_count': trade_count,
                'buy_count': data['buys'],
                'sell_count': data['sells'],
                'buy_volume': round(data['buy_volume'], 2),
                'sell_volume': round(data['sell_volume'], 2),
                'unique_markets': len(data['markets']),
                'is_new_account': is_new,
                'first_trade': data['earliest_trade'].isoformat() if data['earliest_trade'] else None
            })
        
        return results
    
    def _get_activity_gain(self, wallet: str, trades: List[Dict]) -> float:
        """Calculate gain from activity data"""
        # Try to get user activity for more accurate gain calculation
        activities = api.get_user_activity(wallet, limit=100)
        
        if not activities:
            return 0.0
        
        total_gain = 0.0
        for activity in activities:
            activity_type = activity.get('type', '').upper()
            
            if activity_type == 'REDEEM':
                usdc_size = float(activity.get('usdcSize', 0) or activity.get('amount', 0))
                total_gain += usdc_size
            elif activity_type == 'TRADE':
                side = activity.get('side', '').upper()
                usdc_size = float(activity.get('usdcSize', 0) or activity.get('amount', 0))
                if side == 'SELL':
                    total_gain += usdc_size
                elif side == 'BUY':
                    total_gain -= usdc_size
        
        return total_gain
    
    def _apply_filters(
        self,
        accounts: List[Dict],
        min_profit: float,
        max_profit: Optional[float],
        min_trades: int,
        max_trades: Optional[int]
    ) -> List[Dict]:
        """Apply user-selected filters to results"""
        filtered = []
        
        for account in accounts:
            # Use total_gain for profit filtering
            profit = account['total_gain']
            trades = account['trade_count']
            
            # Check min profit
            if profit < min_profit:
                continue
            
            # Check max profit
            if max_profit is not None and profit > max_profit:
                continue
            
            # Check min trades
            if trades < min_trades:
                continue
            
            # Check max trades
            if max_trades is not None and trades > max_trades:
                continue
            
            filtered.append(account)
        
        return filtered
    
    def _sort_results(self, accounts: List[Dict], sort_by: str, sort_order: str) -> List[Dict]:
        """Sort results based on user selection"""
        sort_keys = {
            'profit': lambda x: x['total_gain'],
            'trades': lambda x: x['trade_count'],
            'activity_gain': lambda x: x['activity_gain'],
            'buy_volume': lambda x: x['buy_volume'],
            'sell_volume': lambda x: x['sell_volume'],
            'markets': lambda x: x['unique_markets']
        }
        
        key_func = sort_keys.get(sort_by, sort_keys['profit'])
        reverse = sort_order.lower() == 'desc'
        
        return sorted(accounts, key=key_func, reverse=reverse)
