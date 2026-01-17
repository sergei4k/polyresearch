#!/usr/bin/env python3
"""
Find largest gains among new Polymarket accounts in the last 30 days.

Since Polymarket's API doesn't expose account creation dates, this script
approximates "new accounts" by identifying wallets whose first activity
occurred within the last 30 days.
"""

import requests
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set
from collections import defaultdict
import time


# Polymarket API endpoints
DATA_API_BASE = "https://data-api.polymarket.com"
CLOB_API_BASE = "https://clob.polymarket.com"


class PolymarketGainTracker:
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
    
    def find_top_gainers(self, hours: int = 720, top_n: int = 10) -> List[Dict]:
        """
        Find top gainers among new accounts in the last N hours.
        
        Args:
            hours: Number of hours to look back
            top_n: Number of top gainers to return
        
        Returns:
            List of dictionaries with wallet, gain, and metadata
        """
        print(f"🔍 Analyzing Polymarket activity for the last {hours} hours...")
        
        # Get cutoff time
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        # Step 1: Fetch recent trades
        print("📊 Fetching recent trades...")
        trades = self.get_recent_trades(hours=hours, limit=2000)
        print(f"   Found {len(trades)} trades")
        
        if not trades:
            print("⚠️  No trades found. Check API availability.")
            return []
        
        # Step 2: Extract unique wallets
        wallets = set()
        for trade in trades:
            wallet = trade.get('proxyWallet') or trade.get('user') or trade.get('wallet')
            if wallet:
                wallets.add(wallet)
        
        print(f"   Found {len(wallets)} unique wallets")
        
        # Step 3: Filter for new accounts (those whose first trade is recent)
        print("🆕 Identifying new accounts (first trade in last 30 days)...")
        new_wallets = []
        checked = 0
        
        for wallet in wallets:
            checked += 1
            if checked % 10 == 0:
                print(f"   Checking wallet {checked}/{len(wallets)}...", end='\r')
            
            if self.is_new_account(wallet, cutoff_time, trades):
                new_wallets.append(wallet)
        
        print(f"\n   Found {len(new_wallets)} new accounts")
        
        if not new_wallets:
            print("⚠️  No new accounts found in the specified time period.")
            return []
        
        # Step 4: Calculate gains for new accounts
        print("💰 Calculating gains for new accounts...")
        gains_data = []
        
        for i, wallet in enumerate(new_wallets):
            if (i + 1) % 5 == 0:
                print(f"   Processing {i + 1}/{len(new_wallets)}...", end='\r')
            
            # Calculate gain from trades
            trade_gain = self.calculate_gain_from_trades(wallet, trades)
            
            # Also try to get activity-based gain
            activities = self.get_user_activity(wallet, limit=100)
            activity_gain = self.calculate_gain_from_activity(wallet, activities)
            
            # Use the higher of the two methods (or combine if appropriate)
            total_gain = max(trade_gain, activity_gain)
            
            if total_gain > 0:
                gains_data.append({
                    'wallet': wallet,
                    'gain': total_gain,
                    'trade_gain': trade_gain,
                    'activity_gain': activity_gain,
                    'trade_count': len([t for t in trades if t.get('proxyWallet') == wallet or t.get('user') == wallet]),
                    'activity_count': len(activities)
                })
        
        print(f"\n   Processed {len(new_wallets)} accounts, {len(gains_data)} with positive gains")
        
        # Step 5: Sort by gain and return top N
        gains_data.sort(key=lambda x: x['gain'], reverse=True)
        return gains_data[:top_n]


def format_results(results: List[Dict]) -> str:
    """Format results for display."""
    if not results:
        return "No results found."
    
    output = []
    output.append("=" * 100)
    output.append(f"{'Rank':<6} {'Wallet':<45} {'Gain (USD)':<15} {'Trades':<8} {'Activities':<10}")
    output.append("=" * 100)
    
    for i, result in enumerate(results, 1):
        wallet = result['wallet']
        gain = result['gain']
        trades = result.get('trade_count', 0)
        activities = result.get('activity_count', 0)
        
        # Truncate wallet for display
        wallet_display = wallet[:42] + "..." if len(wallet) > 45 else wallet
        
        output.append(f"{i:<6} {wallet_display:<45} ${gain:>12,.2f} {trades:<8} {activities:<10}")
    
    output.append("=" * 100)
    return "\n".join(output)


def main():
    """Main function."""
    print("\n" + "🚀 Polymarket Top Gainers Tracker")
    print("=" * 100)
    print("\nThis script identifies accounts that:")
    print("  • Had their first activity in the last 30 days")
    print("  • Achieved the largest gains during that period")
    print("\nNote: Account creation dates aren't available via API,")
    print("so we approximate 'new accounts' by checking first activity timestamps.\n")
    
    tracker = PolymarketGainTracker()
    
    # Find top gainers
    top_gainers = tracker.find_top_gainers(hours=720, top_n=20)
    
    if top_gainers:
        print("\n" + format_results(top_gainers))
        
        # Save to file
        output_file = "top_gainers_30d.json"
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'period_hours': 720,
                'results': top_gainers
            }, f, indent=2)
        print(f"\n📄 Results saved to: {output_file}")
    else:
        print("\n⚠️  No gainers found. This could mean:")
        print("  • No new accounts in the last 30 days")
        print("  • API rate limits or availability issues")
        print("  • No accounts with positive gains")


if __name__ == "__main__":
    main()
