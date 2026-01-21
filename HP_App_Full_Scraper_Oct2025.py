"""
================================================================================
HP App - Full Review Scraper (October 2025 onwards)
iOS App Store + Google Play Store - US Market
NO LIMITS - Get ALL available reviews
================================================================================

This scraper collects ALL available reviews since October 2025 for the US market.

Author: Payal
Version: 2.0
Created: January 2026
================================================================================
"""

import json
import csv
import time
import os
from datetime import datetime
from collections import Counter

# Output directory
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# iOS APP STORE SCRAPER (Using app-store-scraper for more reviews)
# ============================================================================

def scrape_ios_reviews():
    """
    Scrape iOS App Store reviews for HP Smart app.
    Uses app-store-scraper library which can get more reviews than RSS feed.
    """
    print("\n" + "="*60)
    print("iOS APP STORE SCRAPER - HP Smart")
    print("Target: ALL US reviews since October 2025")
    print("="*60)

    try:
        from app_store_scraper import AppStore
    except ImportError:
        print("\nERROR: app-store-scraper not installed!")
        print("Install with: pip install app-store-scraper")
        return []

    app_id = 469284907
    app_name = "hp-smart"

    print(f"\nApp ID: {app_id}")
    print(f"App Name: {app_name}")
    print(f"Country: US")
    print(f"Target Date: October 1, 2025 onwards")

    # Initialize scraper
    app = AppStore(country="us", app_name=app_name, app_id=app_id)

    # Scrape reviews - get as many as possible
    # The library will fetch in batches until no more are available
    print("\nFetching reviews (this may take a few minutes)...")

    # Fetch up to 5000 reviews (or all available)
    app.review(how_many=5000)

    all_reviews = app.reviews
    print(f"Total reviews fetched: {len(all_reviews)}")

    # Filter for October 2025 onwards
    oct_2025 = datetime(2025, 10, 1)
    filtered_reviews = []

    for review in all_reviews:
        review_date = review.get('date')
        if review_date and review_date >= oct_2025:
            filtered_reviews.append({
                "id": review.get('id', ''),
                "author": review.get('userName', 'Unknown'),
                "rating": review.get('rating', 0),
                "title": review.get('title', ''),
                "content": review.get('review', ''),
                "version": review.get('version', ''),
                "date": review_date.isoformat() if review_date else '',
                "country": "us",
                "platform": "iOS App Store",
                "vote_count": review.get('voteCount', 0),
                "vote_sum": review.get('voteSum', 0),
            })

    print(f"Reviews from Oct 2025 onwards: {len(filtered_reviews)}")

    return filtered_reviews


# ============================================================================
# GOOGLE PLAY SCRAPER (Increased limit)
# ============================================================================

def scrape_google_play_reviews():
    """
    Scrape Google Play Store reviews for HP Smart app.
    Uses google-play-scraper library.
    """
    print("\n" + "="*60)
    print("GOOGLE PLAY SCRAPER - HP Smart")
    print("Target: ALL US reviews since October 2025")
    print("="*60)

    try:
        from google_play_scraper import reviews, Sort, app as gplay_app
    except ImportError:
        print("\nERROR: google-play-scraper not installed!")
        print("Install with: pip install google-play-scraper")
        return []

    package_id = "com.hp.printercontrol"

    # Get app info
    try:
        app_info = gplay_app(package_id)
        print(f"\nApp: {app_info.get('title')}")
        print(f"Package: {package_id}")
        print(f"Current Rating: {app_info.get('score', 'N/A')}")
        print(f"Total Reviews: {app_info.get('reviews', 'N/A'):,}")
    except:
        print(f"\nPackage: {package_id}")

    print(f"Country: US")
    print(f"Target Date: October 1, 2025 onwards")

    # Fetch reviews in batches
    print("\nFetching reviews (this may take several minutes)...")

    all_reviews = []
    continuation_token = None
    batch_count = 0
    max_batches = 50  # 50 batches x 200 = up to 10,000 reviews

    oct_2025 = datetime(2025, 10, 1)
    reached_old_reviews = False

    while batch_count < max_batches and not reached_old_reviews:
        try:
            result, continuation_token = reviews(
                package_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=200,  # Max per batch
                continuation_token=continuation_token
            )

            if not result:
                break

            batch_count += 1

            for review in result:
                review_date = review.get('at')

                # Check if we've gone past October 2025
                if review_date and review_date < oct_2025:
                    reached_old_reviews = True
                    break

                all_reviews.append({
                    "id": review.get('reviewId', ''),
                    "author": review.get('userName', 'Unknown'),
                    "rating": review.get('score', 0),
                    "title": "",  # Google Play doesn't have titles
                    "content": review.get('content', ''),
                    "version": review.get('reviewCreatedVersion', ''),
                    "date": review_date.isoformat() if review_date else '',
                    "country": "us",
                    "platform": "Google Play",
                    "vote_count": review.get('thumbsUpCount', 0),
                    "reply_content": review.get('replyContent', ''),
                    "reply_date": review.get('repliedAt').isoformat() if review.get('repliedAt') else '',
                })

            print(f"  Batch {batch_count}: {len(result)} reviews (Total: {len(all_reviews)})")

            if continuation_token is None:
                break

            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"  Error in batch {batch_count}: {e}")
            break

    print(f"\nTotal reviews from Oct 2025 onwards: {len(all_reviews)}")

    return all_reviews


# ============================================================================
# ANALYTICS
# ============================================================================

def analyze_reviews(reviews, platform_name):
    """Generate analytics for the reviews"""
    if not reviews:
        return None

    total = len(reviews)
    ratings = [r.get('rating', 0) for r in reviews]
    avg_rating = sum(ratings) / total if total > 0 else 0

    rating_dist = Counter(ratings)

    # Date range
    dates = []
    for r in reviews:
        date_str = r.get('date', '')
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', ''))
                dates.append(dt)
            except:
                pass

    # Version distribution
    version_dist = Counter(r.get('version', 'Unknown') for r in reviews)

    return {
        "platform": platform_name,
        "total_reviews": total,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": dict(sorted(rating_dist.items(), reverse=True)),
        "date_range": {
            "earliest": min(dates).isoformat() if dates else None,
            "latest": max(dates).isoformat() if dates else None,
        },
        "version_distribution": dict(version_dist.most_common(10)),
    }


def print_analytics(analytics):
    """Print analytics summary"""
    print(f"\n{'-'*50}")
    print(f"ANALYTICS: {analytics['platform']}")
    print(f"{'-'*50}")
    print(f"Total Reviews: {analytics['total_reviews']}")
    print(f"Average Rating: {analytics['average_rating']:.2f} / 5.0")

    if analytics['date_range']['earliest']:
        print(f"Date Range: {analytics['date_range']['earliest'][:10]} to {analytics['date_range']['latest'][:10]}")

    print("\nRating Distribution:")
    total = analytics['total_reviews']
    for rating in range(5, 0, -1):
        count = analytics['rating_distribution'].get(rating, 0)
        pct = count / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  {rating}★: {count:5d} ({pct:5.1f}%) {bar}")


# ============================================================================
# SAVE DATA
# ============================================================================

def save_reviews(reviews, json_filename, csv_filename):
    """Save reviews to JSON and CSV"""

    # Save JSON
    json_path = os.path.join(OUTPUT_DIR, json_filename)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False, default=str)
    print(f"✅ Saved: {json_filename} ({len(reviews)} reviews)")

    # Save CSV
    if reviews:
        csv_path = os.path.join(OUTPUT_DIR, csv_filename)
        fieldnames = list(reviews[0].keys())
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(reviews)
        print(f"✅ Saved: {csv_filename}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║     HP SMART APP - FULL REVIEW SCRAPER                        ║
    ║     iOS App Store + Google Play Store                         ║
    ║     US Market | October 2025 onwards | NO LIMITS              ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    all_ios_reviews = []
    all_gplay_reviews = []

    # =========================================================================
    # Scrape iOS
    # =========================================================================
    try:
        ios_reviews = scrape_ios_reviews()
        all_ios_reviews = ios_reviews

        if ios_reviews:
            ios_analytics = analyze_reviews(ios_reviews, "iOS App Store")
            print_analytics(ios_analytics)

            # Save
            save_reviews(ios_reviews,
                        "HP_App_iOS_US_Oct2025_Full.json",
                        "HP_App_iOS_US_Oct2025_Full.csv")

            # Save analytics
            ios_analytics['scrape_date'] = datetime.now().isoformat()
            with open(os.path.join(OUTPUT_DIR, "HP_App_iOS_US_Oct2025_Analytics.json"), 'w') as f:
                json.dump(ios_analytics, f, indent=2)
            print(f"✅ Saved: HP_App_iOS_US_Oct2025_Analytics.json")
    except Exception as e:
        print(f"\n❌ iOS scraping failed: {e}")

    # =========================================================================
    # Scrape Google Play
    # =========================================================================
    try:
        gplay_reviews = scrape_google_play_reviews()
        all_gplay_reviews = gplay_reviews

        if gplay_reviews:
            gplay_analytics = analyze_reviews(gplay_reviews, "Google Play")
            print_analytics(gplay_analytics)

            # Save
            save_reviews(gplay_reviews,
                        "HP_App_GooglePlay_US_Oct2025_Full.json",
                        "HP_App_GooglePlay_US_Oct2025_Full.csv")

            # Save analytics
            gplay_analytics['scrape_date'] = datetime.now().isoformat()
            with open(os.path.join(OUTPUT_DIR, "HP_App_GooglePlay_US_Oct2025_Analytics.json"), 'w') as f:
                json.dump(gplay_analytics, f, indent=2)
            print(f"✅ Saved: HP_App_GooglePlay_US_Oct2025_Analytics.json")
    except Exception as e:
        print(f"\n❌ Google Play scraping failed: {e}")

    # =========================================================================
    # Combined Summary
    # =========================================================================
    print("\n" + "="*60)
    print("SCRAPING COMPLETE - SUMMARY")
    print("="*60)

    total_reviews = len(all_ios_reviews) + len(all_gplay_reviews)

    print(f"""
    iOS App Store:    {len(all_ios_reviews):,} reviews
    Google Play:      {len(all_gplay_reviews):,} reviews
    ─────────────────────────────
    TOTAL:            {total_reviews:,} reviews

    Files Generated:
    ├── HP_App_iOS_US_Oct2025_Full.json
    ├── HP_App_iOS_US_Oct2025_Full.csv
    ├── HP_App_iOS_US_Oct2025_Analytics.json
    ├── HP_App_GooglePlay_US_Oct2025_Full.json
    ├── HP_App_GooglePlay_US_Oct2025_Full.csv
    └── HP_App_GooglePlay_US_Oct2025_Analytics.json
    """)

    # Save combined
    if all_ios_reviews or all_gplay_reviews:
        combined = all_ios_reviews + all_gplay_reviews
        save_reviews(combined,
                    "HP_App_Combined_US_Oct2025_Full.json",
                    "HP_App_Combined_US_Oct2025_Full.csv")

        combined_analytics = analyze_reviews(combined, "Combined (iOS + Android)")
        print_analytics(combined_analytics)

    return all_ios_reviews, all_gplay_reviews


if __name__ == "__main__":
    main()
