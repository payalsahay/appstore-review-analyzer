"""
================================================================================
iOS App Store Scraper - Rolling 30 Days
================================================================================

Scrapes iOS App Store reviews for the last 30 days on a rolling basis.
Each run fetches reviews from (today - 30 days) to today.

App: HP Smart (HP App)
App ID: 469284907
Country: US

Author: Payal
Version: 1.0
Created: January 2026

USAGE:
    python ios_scraper_rolling_30days.py

OUTPUT:
    - data/ios/HP_App_iOS_US_Last30Days.json
    - data/ios/HP_App_iOS_US_Last30Days.csv
    - data/ios/HP_App_iOS_US_Last30Days_Analytics.json

================================================================================
"""

import json
import csv
import os
from datetime import datetime, timedelta
from collections import Counter

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_CONFIG = {
    "app_id": 469284907,
    "app_name": "hp-smart",
    "display_name": "HP App",
    "country": "us",
    "days_back": 30,
}

# Output directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "data", "ios")

# ============================================================================
# iOS SCRAPER
# ============================================================================

def scrape_ios_reviews():
    """
    Scrape iOS App Store reviews for the last 30 days.
    Uses app-store-scraper library.
    """
    print("\n" + "="*60)
    print("iOS APP STORE SCRAPER - ROLLING 30 DAYS")
    print("="*60)

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=APP_CONFIG["days_back"])

    print(f"\nApp: {APP_CONFIG['display_name']}")
    print(f"App ID: {APP_CONFIG['app_id']}")
    print(f"Country: {APP_CONFIG['country'].upper()}")
    print(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"(Rolling {APP_CONFIG['days_back']} days)")

    try:
        from app_store_scraper import AppStore
    except ImportError:
        print("\nERROR: app-store-scraper not installed!")
        print("Install with: pip install app-store-scraper")
        return []

    # Initialize scraper
    print("\nInitializing scraper...")
    app = AppStore(
        country=APP_CONFIG["country"],
        app_name=APP_CONFIG["app_name"],
        app_id=APP_CONFIG["app_id"]
    )

    # Fetch reviews (get more than we need, then filter)
    print("Fetching reviews (this may take a few minutes)...")
    app.review(how_many=3000)  # Fetch up to 3000 to ensure we get all 30-day reviews

    all_reviews = app.reviews
    print(f"Total reviews fetched: {len(all_reviews)}")

    # Filter for last 30 days
    filtered_reviews = []
    for review in all_reviews:
        review_date = review.get('date')
        if review_date and review_date >= start_date:
            filtered_reviews.append({
                "id": str(review.get('id', '')),
                "author": review.get('userName', 'Unknown'),
                "rating": review.get('rating', 0),
                "title": review.get('title', ''),
                "content": review.get('review', ''),
                "version": review.get('version', ''),
                "date": review_date.isoformat() if review_date else '',
                "country": APP_CONFIG["country"],
                "platform": "iOS App Store",
                "vote_count": review.get('voteCount', 0),
                "vote_sum": review.get('voteSum', 0),
            })

    print(f"Reviews in last {APP_CONFIG['days_back']} days: {len(filtered_reviews)}")

    return filtered_reviews


# ============================================================================
# DATA EXPORT
# ============================================================================

def save_to_json(data, filename):
    """Save data to JSON file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"Saved: {filepath}")
    return filepath


def save_to_csv(reviews, filename):
    """Save reviews to CSV file"""
    if not reviews:
        return None

    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fieldnames = ["id", "author", "rating", "title", "content", "version",
                  "date", "country", "platform", "vote_count", "vote_sum"]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviews)

    print(f"Saved: {filepath}")
    return filepath


# ============================================================================
# ANALYTICS
# ============================================================================

def analyze_reviews(reviews):
    """Generate analytics from reviews"""
    if not reviews:
        return None

    total = len(reviews)
    ratings = [r['rating'] for r in reviews]
    avg_rating = sum(ratings) / total if total > 0 else 0

    rating_dist = Counter(ratings)
    version_dist = Counter(r.get('version', 'unknown') for r in reviews if r.get('version'))

    # Date range
    dates = [r['date'] for r in reviews if r.get('date')]

    analytics = {
        "scrape_date": datetime.now().isoformat(),
        "date_range": {
            "days": APP_CONFIG["days_back"],
            "from": min(dates) if dates else None,
            "to": max(dates) if dates else None,
        },
        "total_reviews": total,
        "avg_rating": round(avg_rating, 2),
        "rating_distribution": dict(sorted(rating_dist.items(), reverse=True)),
        "version_distribution": dict(version_dist.most_common(10)),
        "one_star_count": rating_dist.get(1, 0),
        "one_star_pct": round(rating_dist.get(1, 0) / total * 100, 1) if total > 0 else 0,
        "five_star_count": rating_dist.get(5, 0),
        "five_star_pct": round(rating_dist.get(5, 0) / total * 100, 1) if total > 0 else 0,
        "platform": "iOS App Store",
        "country": APP_CONFIG["country"].upper(),
        "app_name": APP_CONFIG["display_name"],
    }

    return analytics


def print_analytics(analytics):
    """Print analytics summary"""
    print("\n" + "="*60)
    print("ANALYTICS SUMMARY")
    print("="*60)

    print(f"\nDate Range: {analytics['date_range']['from'][:10]} to {analytics['date_range']['to'][:10]}")
    print(f"Total Reviews: {analytics['total_reviews']}")
    print(f"Average Rating: {analytics['avg_rating']:.2f} / 5.0")

    print("\nRating Distribution:")
    total = analytics['total_reviews']
    for rating in range(5, 0, -1):
        count = analytics['rating_distribution'].get(rating, 0)
        pct = count / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  {rating} stars: {count:5d} ({pct:5.1f}%) {bar}")

    print("\nTop Versions:")
    for version, count in list(analytics['version_distribution'].items())[:5]:
        if version and version != 'unknown':
            print(f"  v{version}: {count} reviews")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║       iOS APP STORE - ROLLING 30 DAY SCRAPER              ║
    ║                                                           ║
    ║   App: HP App (HP Smart)                                  ║
    ║   App ID: 469284907                                       ║
    ║   Country: US                                             ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Scrape reviews
    reviews = scrape_ios_reviews()

    if not reviews:
        print("\nNo reviews collected.")
        return None

    # Save data
    print("\nSaving data...")
    save_to_json(reviews, "HP_App_iOS_US_Last30Days.json")
    save_to_csv(reviews, "HP_App_iOS_US_Last30Days.csv")

    # Analytics
    analytics = analyze_reviews(reviews)
    print_analytics(analytics)
    save_to_json(analytics, "HP_App_iOS_US_Last30Days_Analytics.json")

    print("\n" + "="*60)
    print("SCRAPING COMPLETE")
    print("="*60)
    print(f"\nFiles saved to: {OUTPUT_DIR}")
    print("  - HP_App_iOS_US_Last30Days.json")
    print("  - HP_App_iOS_US_Last30Days.csv")
    print("  - HP_App_iOS_US_Last30Days_Analytics.json")

    return reviews


if __name__ == "__main__":
    main()
