"""
================================================================================
HPApp_scrapper.py
================================================================================

Advanced App Store Review Scraper for HP Smart / HP App

App: HP (formerly HP Smart)
App ID: 469284907
URL: https://apps.apple.com/us/app/hp/id469284907

Author: Payal
Version: 1.0
Created: January 2026

FEATURES:
- Multi-country scraping (US, UK, CA, AU, IN, DE, FR, JP, etc.)
- RSS feed method (no API key required)
- app-store-scraper library method (more reviews)
- Rate limiting to avoid blocks
- Progress tracking
- Export to CSV and JSON
- Basic analytics

USAGE:
    python HPApp_scrapper.py

OUTPUT:
    - hp_app_reviews.csv
    - hp_app_reviews.json

================================================================================
"""

import requests
import json
import csv
import time
import os
from datetime import datetime
from collections import Counter

# ============================================================================
# HP APP CONFIGURATION
# ============================================================================

APP_CONFIG = {
    "app_id": "469284907",
    "app_name": "hp-smart",
    "display_name": "HP Smart / HP App",
    "bundle_id": "com.hp.printer.control",
    "developer": "HP Inc."
}

# Countries to scrape (ISO 2-letter codes)
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

# Rate limiting
REQUEST_DELAY = 0.5  # seconds between requests
MAX_PAGES_PER_COUNTRY = 10  # RSS feed has max 10 pages (50 reviews each)

# Output directory
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================================
# RSS FEED SCRAPER (No dependencies required)
# ============================================================================

class RSSFeedScraper:
    """
    Scrapes App Store reviews using Apple's RSS feed.
    No API key required. Max ~500 reviews per country.
    """

    def __init__(self, app_id, app_name):
        self.app_id = app_id
        self.app_name = app_name
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

    def get_reviews_page(self, country, page):
        """Fetch a single page of reviews via RSS"""
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={self.app_id}/sortby=mostrecent/json"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            reviews = []
            if "feed" in data and "entry" in data["feed"]:
                entries = data["feed"]["entry"]

                for entry in entries:
                    if "im:rating" in entry:
                        review = {
                            "id": entry.get("id", {}).get("label", ""),
                            "author": entry.get("author", {}).get("name", {}).get("label", "Unknown"),
                            "rating": int(entry.get("im:rating", {}).get("label", 0)),
                            "title": entry.get("title", {}).get("label", ""),
                            "content": entry.get("content", {}).get("label", ""),
                            "version": entry.get("im:version", {}).get("label", ""),
                            "date": entry.get("updated", {}).get("label", ""),
                            "country": country,
                            "vote_count": int(entry.get("im:voteCount", {}).get("label", 0)),
                            "vote_sum": int(entry.get("im:voteSum", {}).get("label", 0)),
                        }
                        reviews.append(review)

            return reviews

        except requests.exceptions.RequestException as e:
            print(f"    Error fetching {country} page {page}: {e}")
            return []
        except json.JSONDecodeError:
            print(f"    Invalid JSON response for {country} page {page}")
            return []

    def scrape_country(self, country, max_pages=10):
        """Scrape all available reviews from a country"""
        all_reviews = []

        for page in range(1, max_pages + 1):
            reviews = self.get_reviews_page(country, page)

            if not reviews:
                break

            all_reviews.extend(reviews)
            print(f"    Page {page}: {len(reviews)} reviews")

            time.sleep(REQUEST_DELAY)

        return all_reviews

    def scrape_all_countries(self, countries, max_pages=10):
        """Scrape reviews from multiple countries"""
        all_reviews = []
        country_stats = {}

        print(f"\n{'='*60}")
        print(f"HP APP REVIEW SCRAPER - RSS Feed Method")
        print(f"App: {APP_CONFIG['display_name']} (ID: {self.app_id})")
        print(f"{'='*60}\n")

        for i, country in enumerate(countries, 1):
            print(f"[{i}/{len(countries)}] Scraping {country.upper()}...")

            reviews = self.scrape_country(country, max_pages)
            country_stats[country] = len(reviews)
            all_reviews.extend(reviews)

            print(f"    Total: {len(reviews)} reviews from {country.upper()}\n")

        print(f"{'='*60}")
        print(f"SCRAPING COMPLETE")
        print(f"Total reviews: {len(all_reviews)}")
        print(f"{'='*60}\n")

        return all_reviews, country_stats


# ============================================================================
# ADVANCED SCRAPER (Using app-store-scraper library)
# ============================================================================

class AdvancedScraper:
    """
    Uses app-store-scraper library for more comprehensive scraping.
    Requires: pip install app-store-scraper
    """

    def __init__(self, app_id, app_name):
        self.app_id = app_id
        self.app_name = app_name

    def scrape_country(self, country, how_many=500):
        """Scrape reviews from a single country"""
        try:
            from app_store_scraper import AppStore

            app = AppStore(
                country=country,
                app_name=self.app_name,
                app_id=self.app_id
            )

            app.review(how_many=how_many)

            reviews = []
            for review in app.reviews:
                review["country"] = country
                reviews.append(review)

            return reviews

        except ImportError:
            print("Error: app-store-scraper not installed.")
            print("Install with: pip install app-store-scraper")
            return []
        except Exception as e:
            print(f"Error scraping {country}: {e}")
            return []

    def scrape_all_countries(self, countries, reviews_per_country=500):
        """Scrape reviews from multiple countries"""
        all_reviews = []
        country_stats = {}

        print(f"\n{'='*60}")
        print(f"HP APP REVIEW SCRAPER - Advanced Method")
        print(f"App: {APP_CONFIG['display_name']} (ID: {self.app_id})")
        print(f"{'='*60}\n")

        for i, country in enumerate(countries, 1):
            print(f"[{i}/{len(countries)}] Scraping {country.upper()}...")

            reviews = self.scrape_country(country, reviews_per_country)
            country_stats[country] = len(reviews)
            all_reviews.extend(reviews)

            print(f"    Collected: {len(reviews)} reviews\n")
            time.sleep(REQUEST_DELAY)

        print(f"{'='*60}")
        print(f"SCRAPING COMPLETE")
        print(f"Total reviews: {len(all_reviews)}")
        print(f"{'='*60}\n")

        return all_reviews, country_stats


# ============================================================================
# DATA EXPORT FUNCTIONS
# ============================================================================

def save_to_json(reviews, filename):
    """Save reviews to JSON file"""
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False, default=str)

    print(f"Saved to: {filepath}")
    return filepath


def save_to_csv(reviews, filename):
    """Save reviews to CSV file"""
    if not reviews:
        print("No reviews to save")
        return None

    filepath = os.path.join(OUTPUT_DIR, filename)

    # Flatten nested fields if any
    flat_reviews = []
    for review in reviews:
        flat_review = {}
        for key, value in review.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_review[f"{key}_{sub_key}"] = sub_value
            else:
                flat_review[key] = value
        flat_reviews.append(flat_review)

    # Get all unique keys
    all_keys = set()
    for review in flat_reviews:
        all_keys.update(review.keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(flat_reviews)

    print(f"Saved to: {filepath}")
    return filepath


# ============================================================================
# ANALYTICS FUNCTIONS
# ============================================================================

def analyze_reviews(reviews):
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

    return {
        "total_reviews": total,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": dict(sorted(rating_dist.items(), reverse=True)),
        "country_distribution": dict(country_dist.most_common()),
        "version_distribution": dict(version_dist.most_common(10)),
    }


def print_analytics(analytics, country_stats):
    """Print analytics to console"""
    print(f"\n{'='*60}")
    print("ANALYTICS SUMMARY")
    print(f"{'='*60}")

    print(f"\nTotal Reviews: {analytics['total_reviews']}")
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
        print(f"  v{version}: {count}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║           HP APP STORE REVIEW SCRAPER                     ║
    ║                                                           ║
    ║   App: HP (formerly HP Smart)                             ║
    ║   ID:  469284907                                          ║
    ║   URL: apps.apple.com/us/app/hp/id469284907               ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Choose scraping method
    print("Select scraping method:")
    print("  1. RSS Feed (No dependencies, ~500 reviews/country)")
    print("  2. Advanced (Requires app-store-scraper, more reviews)")
    print()

    # Default to RSS method
    method = "1"

    try:
        user_input = input("Enter choice [1]: ").strip()
        if user_input in ["1", "2"]:
            method = user_input
    except:
        pass
    
    # Auto-select method 1 (RSS) if no input available
    if not method:
        method = "1"

    # Select countries
    print(f"\nCountries to scrape: {', '.join([c.upper() for c in COUNTRIES[:5]])}...")
    print(f"Total: {len(COUNTRIES)} countries\n")

    # Run scraper
    if method == "1":
        scraper = RSSFeedScraper(APP_CONFIG["app_id"], APP_CONFIG["app_name"])
        reviews, country_stats = scraper.scrape_all_countries(
            COUNTRIES,
            max_pages=MAX_PAGES_PER_COUNTRY
        )
    else:
        scraper = AdvancedScraper(APP_CONFIG["app_id"], APP_CONFIG["app_name"])
        reviews, country_stats = scraper.scrape_all_countries(
            COUNTRIES,
            reviews_per_country=500
        )

    if not reviews:
        print("No reviews collected. Exiting.")
        return

    # Save data
    print("\nSaving data...")
    save_to_json(reviews, "HP_app.json")
    save_to_csv(reviews, "HP_app.csv")

    # Analytics
    analytics = analyze_reviews(reviews)
    print_analytics(analytics, country_stats)

    # Save analytics
    analytics["country_stats"] = country_stats
    analytics["scrape_date"] = datetime.now().isoformat()
    analytics["app_config"] = APP_CONFIG
    save_to_json(analytics, "hp_app_analytics.json")

    print(f"\n{'='*60}")
    print("SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"\nFiles saved to: {OUTPUT_DIR}")
    print("  - HP_app.json")
    print("  - HP_app.csv")
    print("  - hp_app_analytics.json")
    print()


# ============================================================================
# QUICK RUN FUNCTIONS (For importing as module)
# ============================================================================

def quick_scrape(countries=None, max_reviews=500):
    """
    Quick scrape function for importing as module.

    Usage:
        from HPApp_scrapper import quick_scrape
        reviews = quick_scrape(countries=["us", "gb"], max_reviews=200)
    """
    if countries is None:
        countries = ["us"]

    scraper = RSSFeedScraper(APP_CONFIG["app_id"], APP_CONFIG["app_name"])
    reviews, _ = scraper.scrape_all_countries(countries, max_pages=10)

    return reviews


def scrape_and_save(countries=None):
    """
    Scrape and save to files.

    Usage:
        from HPApp_scrapper import scrape_and_save
        scrape_and_save(countries=["us", "gb", "ca"])
    """
    if countries is None:
        countries = COUNTRIES

    scraper = RSSFeedScraper(APP_CONFIG["app_id"], APP_CONFIG["app_name"])
    reviews, country_stats = scraper.scrape_all_countries(countries)

    save_to_json(reviews, "hp_app_reviews.json")
    save_to_csv(reviews, "hp_app_reviews.csv")

    analytics = analyze_reviews(reviews)
    analytics["country_stats"] = country_stats
    save_to_json(analytics, "hp_app_analytics.json")

    return reviews, analytics


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
