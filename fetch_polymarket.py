#!/usr/bin/env python3
"""
Fetch Polymarket event data using the Gamma API (Polymarket Builders Program).

This script fetches event data from Polymarket's public API for the event:
"Who will Trump nominate as Fed Chair?"
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional


# Polymarket Gamma API base URL
GAMMA_API_BASE = "https://gamma-api.polymarket.com"


def fetch_event_by_slug(slug: str) -> Optional[Dict[Any, Any]]:
    """
    Fetch event data by slug using Polymarket Gamma API.
    
    Args:
        slug: The event slug (e.g., 'who-will-trump-nominate-as-fed-chair')
    
    Returns:
        Dictionary containing event data, or None if fetch fails
    """
    url = f"{GAMMA_API_BASE}/events/slug/{slug}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching event data: {e}")
        return None


def fetch_event_by_id(event_id: str) -> Optional[Dict[Any, Any]]:
    """
    Fetch event data by ID using Polymarket Gamma API.
    
    Args:
        event_id: The event ID
    
    Returns:
        Dictionary containing event data, or None if fetch fails
    """
    url = f"{GAMMA_API_BASE}/events/{event_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching event data: {e}")
        return None


def format_event_data(event_data: Dict[Any, Any]) -> str:
    """
    Format event data into a human-readable string.
    
    Args:
        event_data: Dictionary containing event data from API
    
    Returns:
        Formatted string representation of the event data
    """
    if not event_data:
        return "No event data available"
    
    output = []
    output.append("=" * 80)
    output.append(f"Event: {event_data.get('title', 'N/A')}")
    output.append("=" * 80)
    output.append(f"Slug: {event_data.get('slug', 'N/A')}")
    output.append(f"Event ID: {event_data.get('id', 'N/A')}")
    output.append(f"Active: {event_data.get('active', 'N/A')}")
    
    if event_data.get('startDate'):
        start_date = datetime.fromisoformat(event_data['startDate'].replace('Z', '+00:00'))
        output.append(f"Start Date: {start_date}")
    
    if event_data.get('endDate'):
        end_date = datetime.fromisoformat(event_data['endDate'].replace('Z', '+00:00'))
        output.append(f"End Date: {end_date}")
    
    if event_data.get('volume') is not None:
        volume = event_data['volume']
        output.append(f"Volume: ${volume:,.2f}")
    
    if event_data.get('liquidity') is not None:
        liquidity = event_data['liquidity']
        output.append(f"Liquidity: ${liquidity:,.2f}")
    
    # Process markets and outcomes
    markets = event_data.get('markets', [])
    if markets:
        output.append("\n" + "-" * 80)
        output.append("Candidates & Probabilities:")
        output.append("-" * 80)
        output.append(f"{'Candidate':<40} {'Probability':<15} {'Volume':<20}")
        output.append("-" * 80)
        
        # Sort markets by probability (highest first)
        market_list = []
        for market in markets:
            if isinstance(market, dict):
                # Parse outcomes and prices (they may be JSON strings)
                outcomes_str = market.get('outcomes', '[]')
                prices_str = market.get('outcomePrices', '[]')
                
                try:
                    if isinstance(outcomes_str, str):
                        outcomes = json.loads(outcomes_str)
                    else:
                        outcomes = outcomes_str
                    
                    if isinstance(prices_str, str):
                        outcome_prices = json.loads(prices_str)
                    else:
                        outcome_prices = prices_str
                    
                    # Get the "Yes" outcome price (probability)
                    if outcomes and outcome_prices and len(outcomes) > 0:
                        yes_index = outcomes.index('Yes') if 'Yes' in outcomes else 0
                        price = float(outcome_prices[yes_index]) if yes_index < len(outcome_prices) else 0.0
                        prob_percent = price * 100
                        
                        # Get candidate name from groupItemTitle or question
                        candidate = market.get('groupItemTitle', 'N/A')
                        if candidate == 'N/A':
                            # Try to extract from question
                            question = market.get('question', '')
                            # Common pattern: "Will Trump nominate X as..."
                            if 'nominate' in question.lower():
                                parts = question.split('nominate')
                                if len(parts) > 1:
                                    candidate = parts[1].split('as')[0].strip()
                        
                        volume = float(market.get('volume', market.get('volumeNum', 0)))
                        market_list.append((candidate, prob_percent, volume))
                except (json.JSONDecodeError, ValueError, IndexError) as e:
                    # Skip markets we can't parse
                    continue
        
        # Sort by probability (descending)
        market_list.sort(key=lambda x: x[1], reverse=True)
        
        # Display results
        for candidate, prob_percent, volume in market_list:
            output.append(f"{candidate:<40} {prob_percent:>6.2f}%{'':<8} ${volume:>15,.2f}")
    
    output.append("\n" + "=" * 80)
    return "\n".join(output)


def main():
    """Main function to fetch and display Polymarket event data."""
    # Event slug from the URL
    event_slug = "who-will-trump-nominate-as-fed-chair"
    
    print(f"Fetching Polymarket event data for: {event_slug}")
    print(f"API Endpoint: {GAMMA_API_BASE}/events/slug/{event_slug}\n")
    
    # Fetch event data
    event_data = fetch_event_by_slug(event_slug)
    
    if event_data:
        # Display formatted output
        print(format_event_data(event_data))
        
        # Also save raw JSON to file
        output_file = "polymarket_event_data.json"
        with open(output_file, 'w') as f:
            json.dump(event_data, f, indent=2)
        print(f"\nRaw JSON data saved to: {output_file}")
    else:
        print("Failed to fetch event data. Please check your internet connection and the event slug.")


if __name__ == "__main__":
    main()
