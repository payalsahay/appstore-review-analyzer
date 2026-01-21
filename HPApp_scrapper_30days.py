"""
HP App Store Review Scraper - Last 30 Days
Scrapes and filters reviews from the last 30 days only.
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta

APP_CONFIG = {
    "app_id": "469284907",
    "app_name": "hp-smart",
    "display_name": "HP Smart / HP App",
}

COUNTRIES = [
    "us", "gb", "ca", "au", "in", "de", "fr", "jp",
    "br", "mx", "es", "it", "nl", "se", "sg",
]

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
CUTOFF_DATE = datetime.now() - timedelta(days=30)

def parse_date(date_string):
    """Parse various date formats from RSS feed"""
    formats = [
        "%Y-%m-%dT%H:%M:%S-07:00",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_string[:19], fmt[:len(fmt)-len(fmt.split('%')[-1])+2] if '%z' in fmt else fmt)
        except:
            continue
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00').split('+')[0])
    except:
        return None

def scrape_reviews():
    """Scrape HP App reviews from last 30 days"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })

    all_reviews = []

    print(f"\n{'='*60}")
    print(f"HP APP REVIEW SCRAPER - Last 30 Days")
    print(f"App: {APP_CONFIG['display_name']} (ID: {APP_CONFIG['app_id']})")
    print(f"Cutoff Date: {CUTOFF_DATE.strftime('%Y-%m-%d')}")
    print(f"{'='*60}\n")

    for i, country in enumerate(COUNTRIES, 1):
        print(f"[{i}/{len(COUNTRIES)}] Scraping {country.upper()}...")
        country_reviews = []
        stop_scraping = False

        for page in range(1, 11):  # Max 10 pages
            if stop_scraping:
                break

            url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={APP_CONFIG['app_id']}/sortby=mostrecent/json"

            try:
                response = session.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()

                if "feed" not in data or "entry" not in data["feed"]:
                    break

                entries = data["feed"]["entry"]
                page_reviews = 0

                for entry in entries:
                    if "im:rating" not in entry:
                        continue

                    date_str = entry.get("updated", {}).get("label", "")
                    review_date = parse_date(date_str)

                    if review_date and review_date < CUTOFF_DATE:
                        stop_scraping = True
                        break

                    review = {
                        "id": entry.get("id", {}).get("label", ""),
                        "author": entry.get("author", {}).get("name", {}).get("label", "Unknown"),
                        "rating": int(entry.get("im:rating", {}).get("label", 0)),
                        "title": entry.get("title", {}).get("label", ""),
                        "content": entry.get("content", {}).get("label", ""),
                        "version": entry.get("im:version", {}).get("label", ""),
                        "date": date_str,
                        "country": country,
                        "vote_count": int(entry.get("im:voteCount", {}).get("label", 0)),
                        "vote_sum": int(entry.get("im:voteSum", {}).get("label", 0)),
                    }
                    country_reviews.append(review)
                    page_reviews += 1

                if page_reviews > 0:
                    print(f"    Page {page}: {page_reviews} reviews (within 30 days)")

                if page_reviews == 0:
                    break

                time.sleep(0.5)

            except Exception as e:
                print(f"    Error on page {page}: {e}")
                break

        print(f"    Total: {len(country_reviews)} reviews from {country.upper()}\n")
        all_reviews.extend(country_reviews)

    return all_reviews

def analyze_reviews(reviews):
    """Generate analytics"""
    if not reviews:
        return None

    total = len(reviews)
    ratings = [r.get("rating", 0) for r in reviews]
    avg_rating = sum(ratings) / total if total > 0 else 0

    rating_dist = {}
    for r in range(1, 6):
        count = ratings.count(r)
        rating_dist[r] = {"count": count, "percentage": round(count/total*100, 1)}

    country_dist = {}
    for r in reviews:
        c = r.get("country", "unknown")
        country_dist[c] = country_dist.get(c, 0) + 1

    version_dist = {}
    for r in reviews:
        v = r.get("version", "unknown")
        version_dist[v] = version_dist.get(v, 0) + 1

    return {
        "total_reviews": total,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": rating_dist,
        "country_distribution": dict(sorted(country_dist.items(), key=lambda x: x[1], reverse=True)),
        "top_versions": dict(sorted(version_dist.items(), key=lambda x: x[1], reverse=True)[:10]),
    }

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║        HP APP STORE REVIEW SCRAPER - LAST 30 DAYS         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    reviews = scrape_reviews()

    if not reviews:
        print("No reviews collected from last 30 days.")
        return

    # Save reviews
    filepath = os.path.join(OUTPUT_DIR, "HP_app_30.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(reviews)} reviews to: {filepath}")

    # Analytics
    analytics = analyze_reviews(reviews)

    print(f"\n{'='*60}")
    print("LAST 30 DAYS ANALYTICS")
    print(f"{'='*60}")
    print(f"\nTotal Reviews: {analytics['total_reviews']}")
    print(f"Average Rating: {analytics['average_rating']:.2f} / 5.0")

    print("\nRating Distribution:")
    for rating in range(5, 0, -1):
        data = analytics['rating_distribution'].get(rating, {"count": 0, "percentage": 0})
        bar = "█" * int(data['percentage'] / 2)
        print(f"  {rating} stars: {data['count']:4d} ({data['percentage']:5.1f}%) {bar}")

    print("\nTop Countries:")
    for country, count in list(analytics['country_distribution'].items())[:10]:
        print(f"  {country.upper()}: {count}")

    # Save analytics
    analytics["scrape_date"] = datetime.now().isoformat()
    analytics["date_range"] = f"Last 30 days (since {CUTOFF_DATE.strftime('%Y-%m-%d')})"
    analytics_path = os.path.join(OUTPUT_DIR, "HP_app_analytics_30.json")
    with open(analytics_path, "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=2)
    print(f"\nSaved analytics to: {analytics_path}")

if __name__ == "__main__":
    main()
