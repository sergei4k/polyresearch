# Understanding Polymarket Slugs and Data Fetching

## What is a Slug?

A **slug** is a URL-friendly version of a name or title. It's used in web URLs to identify resources in a readable way.

### Examples:

**Event Title:**
- Full title: "Who will Trump nominate as Fed Chair?"
- Slug: `who-will-trump-nominate-as-fed-chair`

**Another Example:**
- Full title: "Will Bitcoin reach $100,000 by end of 2025?"
- Slug: `will-bitcoin-reach-100000-by-end-of-2025`

### Characteristics of Slugs:

1. **Lowercase** - All letters are converted to lowercase
2. **Hyphenated** - Spaces are replaced with hyphens (`-`)
3. **No special characters** - Punctuation, symbols are removed or converted
4. **URL-friendly** - Safe to use in web addresses
5. **Unique identifier** - Each event/market has a unique slug

### Where to Find the Slug:

The slug appears in the Polymarket URL after `/event/`:

```
https://polymarket.com/event/who-will-trump-nominate-as-fed-chair
                                    ↑
                              This is the slug
```

## How to Use the Fetching Functions

The script provides two ways to fetch Polymarket event data:

### Method 1: Fetch by Slug (Recommended)

Use `fetch_event_by_slug()` when you know the slug from the URL:

```python
from fetch_polymarket import fetch_event_by_slug

# Get the slug from the URL
slug = "who-will-trump-nominate-as-fed-chair"

# Fetch the data
event_data = fetch_event_by_slug(slug)

if event_data:
    print(f"Event: {event_data['title']}")
    print(f"Volume: ${event_data['volume']:,.2f}")
else:
    print("Failed to fetch data")
```

**Why use slug?**
- Easy to read and remember
- Can extract directly from URL
- Human-readable identifier

### Method 2: Fetch by ID

Use `fetch_event_by_id()` when you know the numeric event ID:

```python
from fetch_polymarket import fetch_event_by_id

# Event ID is a number (usually from API response)
event_id = "35908"

# Fetch the data
event_data = fetch_event_by_id(event_id)
```

**When to use ID?**
- When you already have the ID from a previous API call
- For programmatic access when ID is already known
- Slightly faster (one less lookup step)

### Complete Usage Example

Here's a practical example showing how to use both methods:

```python
#!/usr/bin/env python3
from fetch_polymarket import fetch_event_by_slug, fetch_event_by_id, format_event_data

# Method 1: Using slug (from URL)
url = "https://polymarket.com/event/who-will-trump-nominate-as-fed-chair"
slug = url.split("/event/")[-1]  # Extract slug from URL
print(f"Extracted slug: {slug}")

event_data = fetch_event_by_slug(slug)
if event_data:
    print("\n" + format_event_data(event_data))
    
    # Method 2: Now we can use the ID from the response
    event_id = event_data['id']
    print(f"\nEvent ID: {event_id}")
    
    # Fetch again using ID (should return same data)
    event_data_by_id = fetch_event_by_id(event_id)
    print(f"Same event? {event_data['title'] == event_data_by_id['title']}")
```

### Extracting Slug from URL

If you have a Polymarket URL, you can extract the slug like this:

```python
def extract_slug_from_url(url):
    """Extract slug from Polymarket event URL."""
    if "/event/" in url:
        return url.split("/event/")[-1].split("?")[0].split("#")[0]
    return None

# Example
url = "https://polymarket.com/event/who-will-trump-nominate-as-fed-chair"
slug = extract_slug_from_url(url)
print(slug)  # Output: who-will-trump-nominate-as-fed-chair
```

### Running the Script

The simplest way to use the fetching functionality:

```bash
# 1. Make sure dependencies are installed
pip install -r requirements.txt

# 2. Run the script (it uses the slug hardcoded in main())
python fetch_polymarket.py
```

To fetch a different event, modify line 163 in `fetch_polymarket.py`:

```python
# Change this line:
event_slug = "who-will-trump-nominate-as-fed-chair"

# To your desired slug:
event_slug = "your-event-slug-here"
```

### API Endpoints Used

The script uses these Polymarket Gamma API endpoints:

1. **By Slug:** `GET https://gamma-api.polymarket.com/events/slug/{slug}`
2. **By ID:** `GET https://gamma-api.polymarket.com/events/{id}`

Both return the same JSON structure with event data, markets, outcomes, prices, volumes, etc.

### What Data You Get

When you fetch an event, you receive:

- **Event metadata**: title, description, dates, active status
- **Volume & liquidity**: total trading volume and liquidity
- **Markets**: all individual markets (outcomes) within the event
- **Prices**: current probability prices for each outcome
- **Trading data**: volumes, 24hr/1wk/1mo statistics

The raw JSON is saved to `polymarket_event_data.json` for further analysis.
