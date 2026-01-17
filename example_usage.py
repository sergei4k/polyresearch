#!/usr/bin/env python3
"""
Example script demonstrating how to use slugs and fetching functions.
"""

from fetch_polymarket import fetch_event_by_slug, fetch_event_by_id, format_event_data


def extract_slug_from_url(url: str) -> str:
    """Extract slug from Polymarket event URL."""
    if "/event/" in url:
        return url.split("/event/")[-1].split("?")[0].split("#")[0]
    return None


def example_1_basic_slug_usage():
    """Example 1: Basic usage with slug."""
    print("=" * 80)
    print("Example 1: Fetching by Slug")
    print("=" * 80)
    
    # The slug is the part after /event/ in the URL
    slug = "who-will-trump-nominate-as-fed-chair"
    print(f"\nSlug: {slug}")
    print(f"This comes from: https://polymarket.com/event/{slug}")
    
    # Fetch the event data
    event_data = fetch_event_by_slug(slug)
    
    if event_data:
        print(f"\n✅ Successfully fetched!")
        print(f"Event Title: {event_data['title']}")
        print(f"Event ID: {event_data['id']}")
        print(f"Volume: ${event_data['volume']:,.2f}")
    else:
        print("\n❌ Failed to fetch event data")
    
    return event_data


def example_2_extract_slug_from_url():
    """Example 2: Extract slug from URL."""
    print("\n" + "=" * 80)
    print("Example 2: Extracting Slug from URL")
    print("=" * 80)
    
    # Example URL
    url = "https://polymarket.com/event/who-will-trump-nominate-as-fed-chair"
    print(f"\nURL: {url}")
    
    # Extract the slug
    slug = extract_slug_from_url(url)
    print(f"Extracted slug: {slug}")
    
    # Now use it to fetch
    event_data = fetch_event_by_slug(slug)
    if event_data:
        print(f"✅ Event found: {event_data['title']}")


def example_3_fetch_by_id():
    """Example 3: Fetching by ID after getting it from slug fetch."""
    print("\n" + "=" * 80)
    print("Example 3: Fetching by ID")
    print("=" * 80)
    
    # First, get the event ID by fetching with slug
    slug = "who-will-trump-nominate-as-fed-chair"
    event_data = fetch_event_by_slug(slug)
    
    if event_data:
        event_id = event_data['id']
        print(f"\nGot Event ID: {event_id} (from slug fetch)")
        
        # Now fetch using the ID
        event_data_by_id = fetch_event_by_id(event_id)
        
        if event_data_by_id:
            print(f"✅ Fetched by ID: {event_data_by_id['title']}")
            print(f"Same event? {event_data['title'] == event_data_by_id['title']}")


def example_4_slug_vs_id():
    """Example 4: Understanding the difference between slug and ID."""
    print("\n" + "=" * 80)
    print("Example 4: Slug vs ID Comparison")
    print("=" * 80)
    
    slug = "who-will-trump-nominate-as-fed-chair"
    
    print(f"\n📝 Slug (human-readable):")
    print(f"   - Format: text with hyphens")
    print(f"   - Example: '{slug}'")
    print(f"   - Source: URL path")
    print(f"   - Use when: You have the URL or remember the event name")
    
    event_data = fetch_event_by_slug(slug)
    if event_data:
        event_id = event_data['id']
        print(f"\n🔢 ID (numeric identifier):")
        print(f"   - Format: number")
        print(f"   - Example: '{event_id}'")
        print(f"   - Source: API response")
        print(f"   - Use when: You already fetched the event and have the ID")
    
    print(f"\n💡 Tip: Slugs are better for human use, IDs are better for programming")


def example_5_formatted_output():
    """Example 5: Displaying formatted output."""
    print("\n" + "=" * 80)
    print("Example 5: Formatted Output")
    print("=" * 80)
    
    slug = "who-will-trump-nominate-as-fed-chair"
    event_data = fetch_event_by_slug(slug)
    
    if event_data:
        print("\n" + format_event_data(event_data))


def main():
    """Run all examples."""
    print("\n" + "🚀 Polymarket Fetching Examples")
    print("=" * 80)
    print("\nThis script demonstrates:")
    print("1. How to use slugs")
    print("2. How to extract slugs from URLs")
    print("3. How to fetch by slug vs ID")
    print("4. The difference between slugs and IDs")
    print("5. How to display formatted results")
    
    # Run examples
    event_data = example_1_basic_slug_usage()
    example_2_extract_slug_from_url()
    example_3_fetch_by_id()
    example_4_slug_vs_id()
    
    # Ask if user wants to see formatted output
    print("\n" + "=" * 80)
    print("Note: Full formatted output is quite long.")
    print("Uncomment example_5_formatted_output() in main() to see it.")
    # example_5_formatted_output()  # Uncomment to see full output


if __name__ == "__main__":
    main()
