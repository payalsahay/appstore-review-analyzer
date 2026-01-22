"""
Apple App Store Review Scraper for Brother Print App
"""

import requests
import json
import csv
from datetime import datetime
import time

# Brother Mobile Connect App ID (from App Store URL)
# URL: https://apps.apple.com/us/app/brother-mobile-connect/id1516235668
APP_ID = "1516235668"
APP_NAME = "brother-mobile-connect"

def get_reviews_via_rss(app_id, country="us", page=1):
    """
    Fetch reviews using Apple's RSS feed (up to 500 reviews per country)
    """
    url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        reviews = []
        if "feed" in data and "entry" in data["feed"]:
            entries = data["feed"]["entry"]
            # First entry is usually app info, skip it
            for entry in entries:
                if "im:rating" in entry:
                    review = {
                        "author": entry.get("author", {}).get("name", {}).get("label", "Unknown"),
                        "rating": int(entry.get("im:rating", {}).get("label", 0)),
                        "title": entry.get("title", {}).get("label", ""),
                        "content": entry.get("content", {}).get("label", ""),
                        "version": entry.get("im:version", {}).get("label", ""),
                        "date": entry.get("updated", {}).get("label", ""),
                        "country": country
                    }
                    reviews.append(review)
        return reviews
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return []


def get_all_reviews_rss(app_id, countries=None, max_pages=10):
    """
    Fetch reviews from multiple countries and pages
    """
    if countries is None:
        countries = ["us", "gb", "ca", "au", "in", "de", "fr", "jp"]

    all_reviews = []

    for country in countries:
        print(f"Fetching reviews from {country.upper()}...")
        for page in range(1, max_pages + 1):
            reviews = get_reviews_via_rss(app_id, country, page)
            if not reviews:
                break
            all_reviews.extend(reviews)
            print(f"  Page {page}: {len(reviews)} reviews")
            time.sleep(0.5)  # Rate limiting

    return all_reviews


def get_reviews_via_api(app_id, country="us", offset=0):
    """
    Alternative method using iTunes API
    """
    url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/json"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def save_to_csv(reviews, filename="brother_print_reviews.csv"):
    """
    Save reviews to CSV file
    """
    if not reviews:
        print("No reviews to save")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=reviews[0].keys())
        writer.writeheader()
        writer.writerows(reviews)

    print(f"Saved {len(reviews)} reviews to {filename}")


def save_to_json(reviews, filename="brother_print_reviews.json"):
    """
    Save reviews to JSON file
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(reviews)} reviews to {filename}")


def analyze_reviews(reviews):
    """
    Basic analysis of scraped reviews
    """
    if not reviews:
        return

    total = len(reviews)
    ratings = [r["rating"] for r in reviews]
    avg_rating = sum(ratings) / total

    rating_dist = {i: ratings.count(i) for i in range(1, 6)}

    print("\n" + "="*50)
    print("REVIEW ANALYSIS")
    print("="*50)
    print(f"Total Reviews: {total}")
    print(f"Average Rating: {avg_rating:.2f}")
    print("\nRating Distribution:")
    for rating, count in sorted(rating_dist.items(), reverse=True):
        bar = "█" * int(count / total * 30)
        print(f"  {rating} stars: {count:4d} ({count/total*100:5.1f}%) {bar}")


def main():
    print("="*50)
    print("Apple App Store Review Scraper")
    print("App: Brother Mobile Connect")
    print("="*50)

    # Fetch reviews
    reviews = get_all_reviews_rss(
        app_id=APP_ID,
        countries=["us", "gb", "ca", "au", "in"],  # Add more country codes as needed
        max_pages=10
    )

    print(f"\nTotal reviews collected: {len(reviews)}")

    # Save results
    save_to_csv(reviews)
    save_to_json(reviews)

    # Analyze
    analyze_reviews(reviews)

    # Print sample reviews
    print("\n" + "="*50)
    print("SAMPLE REVIEWS (First 5)")
    print("="*50)
    for i, review in enumerate(reviews[:5], 1):
        print(f"\n{i}. [{review['rating']}★] {review['title']}")
        print(f"   By: {review['author']} | Version: {review['version']} | Country: {review['country']}")
        print(f"   {review['content'][:200]}...")


if __name__ == "__main__":
    main()
