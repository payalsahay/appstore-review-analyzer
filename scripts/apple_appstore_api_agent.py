"""
================================================================================
Apple App Store Connect API - Review Agent
================================================================================

Fetches ALL iOS App Store reviews using the official App Store Connect API.
This provides complete access to reviews with no limits.

PREREQUISITES:
1. Apple Developer Account with App Store Connect access
2. API Key from App Store Connect (Users and Access > Keys)
3. Download the .p8 private key file

HOW TO GET CREDENTIALS:
1. Go to https://appstoreconnect.apple.com
2. Navigate to: Users and Access > Keys > App Store Connect API
3. Click "+" to generate a new key
4. Select "Admin" or "App Manager" role
5. Download the .p8 file (you can only download it ONCE!)
6. Note your Key ID and Issuer ID from the page

Author: Payal
Version: 1.0
Created: January 2026
================================================================================
"""

import time
import jwt
import requests
import json
import os
from datetime import datetime, timedelta
from collections import Counter

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# From App Store Connect > Users and Access > Keys
KEY_ID = "YOUR_KEY_ID"              # e.g., "ABC123DEFG"
ISSUER_ID = "YOUR_ISSUER_ID"        # e.g., "12345678-1234-1234-1234-123456789012"
PATH_TO_KEY = "AuthKey_XXXX.p8"     # Path to your downloaded .p8 file

# HP Smart App ID (iOS)
APP_ID = "469284907"

# Date filter
SINCE_DATE = datetime(2025, 10, 1)  # Get reviews since October 2025

# Output directory
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# JWT TOKEN GENERATION
# ============================================================================

def generate_token():
    """
    Generates the secure JWT token required by Apple's API.
    Token is valid for 20 minutes.
    """
    try:
        with open(PATH_TO_KEY, 'r') as f:
            private_key = f.read()
    except FileNotFoundError:
        print(f"ERROR: Private key file not found: {PATH_TO_KEY}")
        print("\nPlease ensure you have:")
        print("1. Downloaded the .p8 file from App Store Connect")
        print("2. Updated PATH_TO_KEY with the correct path")
        return None

    headers = {
        'kid': KEY_ID,
        'typ': 'JWT',
        'alg': 'ES256'
    }

    payload = {
        'iss': ISSUER_ID,
        'exp': int(time.time()) + 1200,  # Token valid for 20 mins
        'aud': 'appstoreconnect-v1'
    }

    token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
    return token


# ============================================================================
# REVIEW FETCHER
# ============================================================================

def fetch_all_reviews(territory='US'):
    """
    Fetches all reviews from App Store Connect API.

    Args:
        territory: Country code (default 'US')

    Returns:
        List of review dictionaries
    """
    print("\n" + "="*60)
    print("APPLE APP STORE CONNECT API - REVIEW AGENT")
    print("="*60)
    print(f"\nApp ID: {APP_ID}")
    print(f"Territory: {territory}")
    print(f"Since: {SINCE_DATE.strftime('%Y-%m-%d')}")

    token = generate_token()
    if not token:
        return []

    headers = {'Authorization': f'Bearer {token}'}

    # API endpoint for customer reviews
    url = f"https://api.appstoreconnect.apple.com/v1/apps/{APP_ID}/customerReviews"
    params = {
        'filter[territory]': territory,
        'sort': '-createdDate',  # Newest first
        'limit': 200  # Max per page
    }

    all_reviews = []
    page_count = 0

    print("\nFetching reviews...")

    while url:
        page_count += 1
        print(f"  Page {page_count}: {len(all_reviews)} reviews collected...", end='\r')

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"\nNetwork error: {e}")
            break

        if response.status_code == 401:
            print("\nERROR 401: Authentication failed.")
            print("Please check your KEY_ID, ISSUER_ID, and .p8 file.")
            break
        elif response.status_code == 403:
            print("\nERROR 403: Access forbidden.")
            print("Your API key may not have permission to access reviews.")
            break
        elif response.status_code != 200:
            print(f"\nError: {response.status_code} - {response.text}")
            break

        data = response.json()

        # Process current page
        for item in data.get('data', []):
            attributes = item['attributes']

            # Parse date
            try:
                review_date = datetime.fromisoformat(
                    attributes['createdDate'].replace('Z', '+00:00')
                )
            except:
                continue

            # Stop if we've reached reviews older than our target date
            if review_date.replace(tzinfo=None) < SINCE_DATE:
                print(f"\n\nReached {SINCE_DATE.strftime('%B %Y')} cutoff. Stopping.")
                return all_reviews

            # Format review for analysis
            clean_review = {
                "id": item['id'],
                "date": attributes['createdDate'],
                "rating": attributes['rating'],
                "title": attributes.get('title', ''),
                "content": attributes.get('body', ''),
                "territory": attributes['territory'],
                "platform": "iOS App Store",
                "country": territory.lower(),
            }
            all_reviews.append(clean_review)

        # Handle pagination
        links = data.get('links', {})
        url = links.get('next')  # Get next page URL
        params = None  # Params are included in 'next' URL

        # Regenerate token if needed (every 15 minutes to be safe)
        if page_count % 50 == 0:
            print("\n  Refreshing API token...")
            token = generate_token()
            if token:
                headers = {'Authorization': f'Bearer {token}'}

    print(f"\n\nTotal reviews collected: {len(all_reviews)}")
    return all_reviews


# ============================================================================
# ANALYTICS
# ============================================================================

def analyze_reviews(reviews):
    """Generate basic analytics from reviews"""
    if not reviews:
        return None

    total = len(reviews)
    ratings = [r['rating'] for r in reviews]
    avg_rating = sum(ratings) / total

    rating_dist = Counter(ratings)

    # Date range
    dates = [r['date'] for r in reviews]

    analytics = {
        "total_reviews": total,
        "avg_rating": round(avg_rating, 2),
        "rating_distribution": dict(sorted(rating_dist.items(), reverse=True)),
        "date_range": {
            "from": min(dates),
            "to": max(dates)
        },
        "one_star_pct": round(rating_dist.get(1, 0) / total * 100, 1),
        "five_star_pct": round(rating_dist.get(5, 0) / total * 100, 1),
    }

    return analytics


def print_analytics(analytics):
    """Print analytics summary"""
    print("\n" + "="*60)
    print("ANALYTICS SUMMARY")
    print("="*60)

    print(f"\nTotal Reviews: {analytics['total_reviews']}")
    print(f"Average Rating: {analytics['avg_rating']:.2f} / 5.0")
    print(f"Date Range: {analytics['date_range']['from'][:10]} to {analytics['date_range']['to'][:10]}")

    print("\nRating Distribution:")
    total = analytics['total_reviews']
    for rating in range(5, 0, -1):
        count = analytics['rating_distribution'].get(rating, 0)
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"  {rating} stars: {count:5d} ({pct:5.1f}%) {bar}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     APPLE APP STORE CONNECT API - REVIEW AGENT            ║
    ║                                                           ║
    ║   App: HP Smart (HP App)                                  ║
    ║   App ID: 469284907                                       ║
    ║   Target: US reviews since October 2025                   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Check configuration
    if KEY_ID == "YOUR_KEY_ID" or ISSUER_ID == "YOUR_ISSUER_ID":
        print("ERROR: Please configure your API credentials!")
        print("\nEdit this file and update:")
        print("  - KEY_ID")
        print("  - ISSUER_ID")
        print("  - PATH_TO_KEY")
        print("\nSee instructions at top of file for how to get these.")
        return

    # Fetch reviews
    reviews = fetch_all_reviews(territory='US')

    if not reviews:
        print("\nNo reviews collected. Please check your configuration.")
        return

    # Save reviews
    output_file = os.path.join(OUTPUT_DIR, "..", "data", "ios", "HP_App_iOS_US_Oct2025_API.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    print(f"\nSaved reviews to: {output_file}")

    # Analytics
    analytics = analyze_reviews(reviews)
    print_analytics(analytics)

    # Save analytics
    analytics_file = os.path.join(OUTPUT_DIR, "..", "data", "ios", "HP_App_iOS_US_Oct2025_API_Analytics.json")
    analytics['scrape_date'] = datetime.now().isoformat()
    analytics['source'] = 'App Store Connect API'

    with open(analytics_file, 'w') as f:
        json.dump(analytics, f, indent=2)
    print(f"Saved analytics to: {analytics_file}")

    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
