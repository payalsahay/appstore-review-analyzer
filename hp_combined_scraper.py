import pandas as pd
from datetime import datetime
from google_play_scraper import reviews, Sort
from app_store_scraper import AppStore
import time

# --- CONFIGURATION ---
TARGET_DATE = datetime(2025, 10, 1)
OUTPUT_FILE = "hp_app_reviews_oct2025_present.csv"

# --- UPDATED APP IDENTIFIERS ---
# Google Play still uses the old package name internally
GOOGLE_PLAY_ID = 'com.hp.printercontrol'

# Apple updated the URL slug to 'hp', but the ID remains the same
APP_STORE_ID = '469284907'
APP_STORE_NAME = 'hp'

def scrape_google_play():
    print(f"--- Scraping Google Play Store (ID: {GOOGLE_PLAY_ID}) ---")
    all_reviews = []
    continuation_token = None

    keep_scraping = True
    batch_count = 0

    while keep_scraping:
        result, continuation_token = reviews(
            GOOGLE_PLAY_ID,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=200,
            continuation_token=continuation_token
        )

        if not result:
            break

        for review in result:
            review_date = review['at']
            if review_date >= TARGET_DATE:
                all_reviews.append({
                    'source': 'Google Play',
                    'date': review_date,
                    'rating': review['score'],
                    'content': review['content'],
                    'title': None,
                    'version': review.get('reviewCreatedVersion') # Useful to see if they are on the new version
                })
            else:
                keep_scraping = False
                break

        batch_count += 1
        print(f"Batch {batch_count}: Collected {len(all_reviews)} valid reviews...")

        if continuation_token is None:
            break

    return all_reviews

def scrape_app_store():
    print(f"\n--- Scraping Apple App Store (App Name: '{APP_STORE_NAME}') ---")

    # We use 'hp' as the app_name now to match the new URL structure
    hp_app = AppStore(country='us', app_name=APP_STORE_NAME, app_id=APP_STORE_ID)

    hp_app.review(how_many=2000, sleep=1)

    filtered_reviews = []
    print(f"Total reviews fetched: {len(hp_app.reviews)}")

    for review in hp_app.reviews:
        review_date = review['date']
        if review_date >= TARGET_DATE:
            filtered_reviews.append({
                'source': 'App Store',
                'date': review_date,
                'rating': review['rating'],
                'content': review['review'],
                'title': review['title'],
                'version': None # Apple scraper often doesn't return version in this list
            })

    return filtered_reviews

if __name__ == "__main__":
    print(f"Starting scrape for 'HP' App (since {TARGET_DATE.strftime('%Y-%m-%d')})...")

    # 1. Scrape
    gp_data = scrape_google_play()
    apple_data = scrape_app_store()

    # 2. Combine
    combined_data = gp_data + apple_data

    # 3. Save
    if combined_data:
        df = pd.DataFrame(combined_data)
        df.sort_values(by='date', ascending=False, inplace=True)

        print(f"\nTotal Reviews Found: {len(df)}")
        print(f"Breakdown: {len(gp_data)} from Google Play, {len(apple_data)} from App Store")

        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Successfully saved to {OUTPUT_FILE}")
    else:
        print("\nNo reviews found for the specified period.")
