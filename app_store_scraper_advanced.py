"""
Advanced Apple App Store Review Scraper using RSS feed method
Uses Apple's public RSS feed (more reliable than private API)
"""

import requests
import pandas as pd
import json
from datetime import datetime
import time

# Brother Mobile Connect App ID
APP_ID = "1516235668"


def scrape_brother_print_reviews(country="us", how_many=None, max_pages=10):
    """
    Scrape reviews using Apple's RSS feed (more reliable than app-store-scraper library)
    
    Args:
        country: Country code (us, gb, ca, au, in, de, fr, jp, etc.)
        how_many: Number of reviews to fetch (optional, if None fetches all available pages)
        max_pages: Maximum pages to fetch per country (default 10, max 10 pages = ~500 reviews)
    """
    print(f"Scraping reviews from {country.upper()}...")
    
    all_reviews = []
    # If how_many is specified, calculate max_pages; otherwise use max_pages directly
    if how_many is not None:
        calculated_pages = min((how_many // 50) + 1, 10)
        max_pages = min(calculated_pages, max_pages)
    else:
        max_pages = min(max_pages, 10)  # Max 10 pages, 50 reviews per page
    
    for page in range(1, max_pages + 1):
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={APP_ID}/sortby=mostrecent/json"
        
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
                        # Convert to format similar to app-store-scraper
                        review = {
                            "title": entry.get("title", {}).get("label", ""),
                            "review": entry.get("content", {}).get("label", ""),
                            "rating": int(entry.get("im:rating", {}).get("label", 0)),
                            "userName": entry.get("author", {}).get("name", {}).get("label", "Unknown"),
                            "date": entry.get("updated", {}).get("label", ""),
                            "version": entry.get("im:version", {}).get("label", ""),
                            "country": country
                        }
                        reviews.append(review)
            
            if not reviews:
                break
                
            all_reviews.extend(reviews)
            print(f"  Page {page}: {len(reviews)} reviews")
            
            if how_many is not None and len(all_reviews) >= how_many:
                break
                
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  Error on page {page}: {e}")
            break
    
    print(f"Fetched {len(all_reviews)} reviews from {country.upper()}")
    # Only limit if how_many was specified
    if how_many is not None:
        return all_reviews[:how_many]
    return all_reviews


def scrape_multiple_countries(countries=None, reviews_per_country=None, max_pages=10):
    """
    Scrape reviews from multiple countries
    
    Args:
        countries: List of country codes to scrape from
        reviews_per_country: Number of reviews per country (None = fetch all available pages)
        max_pages: Maximum pages to fetch per country (default 10)
    """
    if countries is None:
        countries = ["us", "gb", "ca", "au", "in", "de", "fr", "jp", "br", "mx"]

    all_reviews = []

    for country in countries:
        try:
            reviews = scrape_brother_print_reviews(country, reviews_per_country, max_pages)
            # Country info is already added in scrape_brother_print_reviews
            all_reviews.extend(reviews)
        except Exception as e:
            print(f"Error scraping {country}: {e}")

    return all_reviews


def save_reviews(reviews, base_filename="brother_print_reviews"):
    """
    Save reviews to CSV and JSON
    """
    if not reviews:
        print("No reviews to save")
        return

    # Convert to DataFrame
    df = pd.DataFrame(reviews)

    # Save to CSV
    csv_file = f"{base_filename}.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8")
    print(f"Saved to {csv_file}")

    # Save to JSON
    json_file = f"{base_filename}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2, default=str, ensure_ascii=False)
    print(f"Saved to {json_file}")

    return df


def analyze_reviews(df):
    """
    Analyze the scraped reviews
    """
    print("\n" + "="*60)
    print("REVIEW ANALYSIS - Brother Mobile Connect")
    print("="*60)

    print(f"\nTotal Reviews: {len(df)}")
    print(f"Average Rating: {df['rating'].mean():.2f}")

    print("\nRating Distribution:")
    rating_counts = df['rating'].value_counts().sort_index(ascending=False)
    for rating, count in rating_counts.items():
        pct = count / len(df) * 100
        bar = "█" * int(pct / 2)
        print(f"  {rating} stars: {count:5d} ({pct:5.1f}%) {bar}")

    if "country" in df.columns:
        print("\nReviews by Country:")
        country_counts = df["country"].value_counts()
        for country, count in country_counts.items():
            print(f"  {country.upper()}: {count}")

    print("\nDate Range:")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        print(f"  Oldest: {df['date'].min()}")
        print(f"  Newest: {df['date'].max()}")


def print_sample_reviews(reviews, n=5):
    """
    Print sample reviews
    """
    print("\n" + "="*60)
    print(f"SAMPLE REVIEWS (First {n})")
    print("="*60)

    for i, review in enumerate(reviews[:n], 1):
        print(f"\n{i}. [{review.get('rating', 'N/A')}★] {review.get('title', 'No title')}")
        print(f"   By: {review.get('userName', 'Unknown')}")
        print(f"   Date: {review.get('date', 'Unknown')}")
        print(f"   Country: {review.get('country', 'Unknown').upper()}")
        content = review.get('review', '')[:300]
        print(f"   {content}...")


def main():
    print("="*60)
    print("Advanced App Store Review Scraper")
    print("App: Brother Mobile Connect (ID: 1516235668)")
    print("="*60)

    # Option 1: Scrape from single country
    # reviews = scrape_brother_print_reviews(country="us", how_many=1000)

    # Option 2: Scrape from multiple countries (fetch all available pages, up to 10 per country)
    reviews = scrape_multiple_countries(
        countries=["us", "gb", "ca", "au", "in"],
        max_pages=10  # Match simple scraper: 10 pages per country
    )

    print(f"\nTotal reviews collected: {len(reviews)}")

    # Save reviews
    df = save_reviews(reviews)

    # Analyze
    if df is not None and not df.empty:
        analyze_reviews(df)

    # Print samples
    print_sample_reviews(reviews)


if __name__ == "__main__":
    main()
