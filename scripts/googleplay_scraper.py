"""
================================================================================
GooglePlay_HPApp_scraper.py
================================================================================

Google Play Store Review Scraper for HP Smart / HP App

App: HP Smart
Package ID: com.hp.printercontrol
URL: https://play.google.com/store/apps/details?id=com.hp.printercontrol

Author: Payal
Version: 1.0
Created: January 2026

FEATURES:
- Multi-country scraping
- Uses google-play-scraper library
- Rate limiting to avoid blocks
- Progress tracking
- Export to CSV and JSON
- Basic analytics (matching iOS format)

REQUIREMENTS:
    pip install google-play-scraper

USAGE:
    python GooglePlay_HPApp_scraper.py

OUTPUT:
    - GooglePlay_HP_app.csv
    - GooglePlay_HP_app.json
    - GooglePlay_HP_app_analytics.json

================================================================================
"""

import json
import csv
import time
import os
from datetime import datetime
from collections import Counter

# ============================================================================
# HP APP CONFIGURATION (Google Play)
# ============================================================================

APP_CONFIG = {
    "package_id": "com.hp.printercontrol",
    "app_name": "HP Smart",
    "display_name": "HP Smart",
    "developer": "HP Inc.",
    "store": "Google Play"
}

# Countries to scrape (ISO 2-letter codes)
# Note: Google Play uses 'en' for language, country codes for region
COUNTRIES = [
    "us",  # United States
    "gb",  # United Kingdom
    "ca",  # Canada
    "au",  # Australia
    "in",  # India
    "de",  # Germany
    "fr",  # France
    "jp",  # Japan
    "br",  # Brazil
    "mx",  # Mexico
    "es",  # Spain
    "it",  # Italy
    "nl",  # Netherlands
    "se",  # Sweden
    "sg",  # Singapore
]

# Language mapping for countries
COUNTRY_LANGUAGE_MAP = {
    "us": "en",
    "gb": "en",
    "ca": "en",
    "au": "en",
    "in": "en",
    "de": "de",
    "fr": "fr",
    "jp": "ja",
    "br": "pt",
    "mx": "es",
    "es": "es",
    "it": "it",
    "nl": "nl",
    "se": "sv",
    "sg": "en",
}

# Rate limiting
REQUEST_DELAY = 1.0  # seconds between requests (Google is stricter)
REVIEWS_PER_COUNTRY = 500  # Number of reviews to fetch per country

# Output directory
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================================
# GOOGLE PLAY SCRAPER
# ============================================================================

class GooglePlayScraper:
    """
    Scrapes Google Play Store reviews using google-play-scraper library.
    Requires: pip install google-play-scraper
    """

    def __init__(self, package_id):
        self.package_id = package_id
        self._check_dependency()

    def _check_dependency(self):
        """Check if google-play-scraper is installed"""
        try:
            from google_play_scraper import reviews, Sort
            self.reviews_func = reviews
            self.Sort = Sort
            return True
        except ImportError:
            print("=" * 60)
            print("ERROR: google-play-scraper not installed!")
            print("=" * 60)
            print("\nPlease install it with:")
            print("  pip install google-play-scraper")
            print()
            raise ImportError("google-play-scraper is required")

    def get_app_info(self):
        """Get app details from Google Play"""
        try:
            from google_play_scraper import app
            info = app(self.package_id)
            return {
                "title": info.get("title"),
                "developer": info.get("developer"),
                "rating": info.get("score"),
                "reviews_count": info.get("reviews"),
                "installs": info.get("installs"),
                "version": info.get("version"),
                "updated": info.get("updated"),
                "description_short": info.get("summary"),
            }
        except Exception as e:
            print(f"Warning: Could not fetch app info: {e}")
            return None

    def scrape_country(self, country, lang=None, count=500):
        """
        Scrape reviews from a single country/language.

        Args:
            country: Country code (e.g., 'us', 'gb')
            lang: Language code (e.g., 'en', 'de'). If None, uses mapping.
            count: Number of reviews to fetch

        Returns:
            List of review dictionaries
        """
        if lang is None:
            lang = COUNTRY_LANGUAGE_MAP.get(country, "en")

        all_reviews = []
        continuation_token = None
        batch_size = 100  # Google Play returns max 100 per request

        try:
            fetched = 0
            while fetched < count:
                # Fetch batch of reviews
                result, continuation_token = self.reviews_func(
                    self.package_id,
                    lang=lang,
                    country=country,
                    sort=self.Sort.NEWEST,
                    count=min(batch_size, count - fetched),
                    continuation_token=continuation_token
                )

                if not result:
                    break

                # Process reviews
                for review in result:
                    processed = {
                        "id": review.get("reviewId", ""),
                        "author": review.get("userName", "Unknown"),
                        "rating": review.get("score", 0),
                        "title": "",  # Google Play doesn't have titles
                        "content": review.get("content", ""),
                        "version": review.get("reviewCreatedVersion", ""),
                        "date": review.get("at").isoformat() if review.get("at") else "",
                        "country": country,
                        "language": lang,
                        "vote_count": review.get("thumbsUpCount", 0),
                        "reply_content": review.get("replyContent", ""),
                        "reply_date": review.get("repliedAt").isoformat() if review.get("repliedAt") else "",
                    }
                    all_reviews.append(processed)

                fetched += len(result)
                print(f"    Fetched {fetched} reviews...")

                if continuation_token is None:
                    break

                time.sleep(REQUEST_DELAY)

            return all_reviews

        except Exception as e:
            print(f"    Error scraping {country}: {e}")
            return all_reviews

    def scrape_all_countries(self, countries, reviews_per_country=500):
        """Scrape reviews from multiple countries"""
        all_reviews = []
        country_stats = {}

        print(f"\n{'='*60}")
        print(f"HP APP REVIEW SCRAPER - Google Play Store")
        print(f"App: {APP_CONFIG['display_name']}")
        print(f"Package: {self.package_id}")
        print(f"{'='*60}\n")

        # Get app info first
        app_info = self.get_app_info()
        if app_info:
            print("App Information:")
            print(f"  Title: {app_info.get('title')}")
            print(f"  Rating: {app_info.get('rating'):.2f}")
            print(f"  Total Reviews: {app_info.get('reviews_count'):,}")
            print(f"  Installs: {app_info.get('installs')}")
            print(f"  Version: {app_info.get('version')}")
            print()

        for i, country in enumerate(countries, 1):
            print(f"[{i}/{len(countries)}] Scraping {country.upper()}...")

            reviews = self.scrape_country(country, count=reviews_per_country)
            country_stats[country] = len(reviews)
            all_reviews.extend(reviews)

            print(f"    Total: {len(reviews)} reviews from {country.upper()}\n")
            time.sleep(REQUEST_DELAY)

        print(f"{'='*60}")
        print(f"SCRAPING COMPLETE")
        print(f"Total reviews: {len(all_reviews)}")
        print(f"{'='*60}\n")

        return all_reviews, country_stats, app_info


# ============================================================================
# DATA EXPORT FUNCTIONS
# ============================================================================

def save_to_json(data, filename):
    """Save data to JSON file"""
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"Saved to: {filepath}")
    return filepath


def save_to_csv(reviews, filename):
    """Save reviews to CSV file"""
    if not reviews:
        print("No reviews to save")
        return None

    filepath = os.path.join(OUTPUT_DIR, filename)

    # Get all unique keys
    all_keys = set()
    for review in reviews:
        all_keys.update(review.keys())

    # Define preferred column order
    preferred_order = [
        "id", "author", "rating", "title", "content", "version",
        "date", "country", "language", "vote_count", "reply_content", "reply_date"
    ]

    # Sort keys with preferred order first
    fieldnames = [k for k in preferred_order if k in all_keys]
    fieldnames += sorted([k for k in all_keys if k not in preferred_order])

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviews)

    print(f"Saved to: {filepath}")
    return filepath


# ============================================================================
# ANALYTICS FUNCTIONS
# ============================================================================

def analyze_reviews(reviews, app_info=None):
    """Generate basic analytics from reviews"""
    if not reviews:
        return None

    total = len(reviews)
    ratings = [r.get("rating", 0) for r in reviews]
    avg_rating = sum(ratings) / total if total > 0 else 0

    rating_dist = Counter(ratings)
    country_dist = Counter(r.get("country", "unknown") for r in reviews)

    # Version distribution
    version_dist = Counter(r.get("version", "unknown") for r in reviews)

    # Reviews with developer replies
    replies = sum(1 for r in reviews if r.get("reply_content"))
    reply_rate = replies / total * 100 if total > 0 else 0

    analytics = {
        "total_reviews": total,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": dict(sorted(rating_dist.items(), reverse=True)),
        "country_distribution": dict(country_dist.most_common()),
        "version_distribution": dict(version_dist.most_common(10)),
        "developer_replies": replies,
        "reply_rate_percent": round(reply_rate, 1),
    }

    if app_info:
        analytics["app_info"] = app_info

    return analytics


def print_analytics(analytics, country_stats):
    """Print analytics to console"""
    print(f"\n{'='*60}")
    print("ANALYTICS SUMMARY")
    print(f"{'='*60}")

    print(f"\nTotal Reviews Collected: {analytics['total_reviews']}")
    print(f"Average Rating: {analytics['average_rating']:.2f} / 5.0")

    print("\nRating Distribution:")
    total = analytics["total_reviews"]
    for rating in range(5, 0, -1):
        count = analytics["rating_distribution"].get(rating, 0)
        pct = count / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  {rating} stars: {count:5d} ({pct:5.1f}%) {bar}")

    print("\nReviews by Country:")
    for country, count in list(analytics["country_distribution"].items())[:10]:
        print(f"  {country.upper()}: {count}")

    print("\nTop App Versions:")
    for version, count in list(analytics["version_distribution"].items())[:5]:
        if version and version != "unknown":
            print(f"  v{version}: {count}")

    print(f"\nDeveloper Response Rate: {analytics['reply_rate_percent']}%")
    print(f"  ({analytics['developer_replies']} reviews with replies)")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║       GOOGLE PLAY STORE - HP APP REVIEW SCRAPER           ║
    ║                                                           ║
    ║   App: HP Smart                                           ║
    ║   Package: com.hp.printercontrol                          ║
    ║   URL: play.google.com/store/apps/details?id=...          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Configuration
    print(f"Countries to scrape: {', '.join([c.upper() for c in COUNTRIES[:5]])}...")
    print(f"Total: {len(COUNTRIES)} countries")
    print(f"Reviews per country: {REVIEWS_PER_COUNTRY}")
    print()

    # Initialize scraper
    try:
        scraper = GooglePlayScraper(APP_CONFIG["package_id"])
    except ImportError:
        return

    # Run scraper
    reviews, country_stats, app_info = scraper.scrape_all_countries(
        COUNTRIES,
        reviews_per_country=REVIEWS_PER_COUNTRY
    )

    if not reviews:
        print("No reviews collected. Exiting.")
        return

    # Save data
    print("\nSaving data...")
    save_to_json(reviews, "GooglePlay_HP_app.json")
    save_to_csv(reviews, "GooglePlay_HP_app.csv")

    # Analytics
    analytics = analyze_reviews(reviews, app_info)
    print_analytics(analytics, country_stats)

    # Save analytics
    analytics["country_stats"] = country_stats
    analytics["scrape_date"] = datetime.now().isoformat()
    analytics["app_config"] = APP_CONFIG
    save_to_json(analytics, "GooglePlay_HP_app_analytics.json")

    print(f"\n{'='*60}")
    print("SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"\nFiles saved to: {OUTPUT_DIR}")
    print("  - GooglePlay_HP_app.json")
    print("  - GooglePlay_HP_app.csv")
    print("  - GooglePlay_HP_app_analytics.json")
    print()


# ============================================================================
# QUICK RUN FUNCTIONS (For importing as module)
# ============================================================================

def quick_scrape(countries=None, max_reviews=500):
    """
    Quick scrape function for importing as module.

    Usage:
        from GooglePlay_HPApp_scraper import quick_scrape
        reviews = quick_scrape(countries=["us", "gb"], max_reviews=200)
    """
    if countries is None:
        countries = ["us"]

    scraper = GooglePlayScraper(APP_CONFIG["package_id"])
    reviews, _, _ = scraper.scrape_all_countries(countries, reviews_per_country=max_reviews)

    return reviews


def scrape_and_save(countries=None, reviews_per_country=500):
    """
    Scrape and save to files.

    Usage:
        from GooglePlay_HPApp_scraper import scrape_and_save
        scrape_and_save(countries=["us", "gb", "ca"])
    """
    if countries is None:
        countries = COUNTRIES

    scraper = GooglePlayScraper(APP_CONFIG["package_id"])
    reviews, country_stats, app_info = scraper.scrape_all_countries(
        countries,
        reviews_per_country=reviews_per_country
    )

    save_to_json(reviews, "GooglePlay_HP_app.json")
    save_to_csv(reviews, "GooglePlay_HP_app.csv")

    analytics = analyze_reviews(reviews, app_info)
    analytics["country_stats"] = country_stats
    save_to_json(analytics, "GooglePlay_HP_app_analytics.json")

    return reviews, analytics


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
