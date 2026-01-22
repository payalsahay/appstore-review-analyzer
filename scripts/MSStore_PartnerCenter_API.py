"""
================================================================================
MSStore_PartnerCenter_API.py
================================================================================

Microsoft Store Partner Center Analytics API - Review Scraper

This module uses the official Microsoft Store Analytics API to retrieve
app reviews. IMPORTANT: This requires Partner Center access for the app.

API Documentation:
https://learn.microsoft.com/en-us/windows/uwp/monetize/get-app-reviews

REQUIREMENTS:
1. Microsoft Partner Center account with access to the app
2. Azure AD App Registration with proper permissions
3. Client ID, Client Secret, and Tenant ID

SETUP STEPS:
1. Go to Azure Portal (portal.azure.com)
2. Register an Azure AD application
3. Associate it with your Partner Center account
4. Grant "Windows Store analytics" permission
5. Create a client secret
6. Copy Tenant ID, Client ID, and Client Secret

Author: Payal
Version: 1.0
Created: January 2026

================================================================================
"""

import requests
import json
import csv
import os
from datetime import datetime, timedelta
from collections import Counter

# ============================================================================
# CONFIGURATION - FILL IN YOUR CREDENTIALS
# ============================================================================

# Azure AD / Partner Center Credentials
# Get these from Azure Portal after registering your app
CONFIG = {
    "tenant_id": "YOUR_TENANT_ID",           # Azure AD Tenant ID
    "client_id": "YOUR_CLIENT_ID",           # Azure AD Application (client) ID
    "client_secret": "YOUR_CLIENT_SECRET",   # Azure AD Client Secret

    # HP Smart App ID on Microsoft Store
    # You can only access this if you own the app in Partner Center
    "app_id": "9wzdncrfhwlh",
    "app_name": "HP Smart"
}

# API Endpoints
ENDPOINTS = {
    "token": "https://login.microsoftonline.com/{tenant_id}/oauth2/token",
    "reviews": "https://manage.devcenter.microsoft.com/v1.0/my/analytics/reviews"
}

# Output directory
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================================
# AUTHENTICATION
# ============================================================================

class PartnerCenterAuth:
    """
    Handles Azure AD authentication for Partner Center API.
    """

    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = None

    def get_access_token(self):
        """
        Obtain Azure AD access token for Partner Center API.
        Token is valid for 60 minutes.
        """
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        token_url = ENDPOINTS["token"].format(tenant_id=self.tenant_id)

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "resource": "https://manage.devcenter.microsoft.com"
        }

        try:
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]

            # Token expires in ~3600 seconds, refresh 5 mins early
            expires_in = int(token_data.get("expires_in", 3600)) - 300
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

            return self.access_token

        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = response.json()
            except:
                error_detail = response.text

            raise Exception(f"Failed to get access token: {e}\nDetails: {error_detail}")

        except Exception as e:
            raise Exception(f"Authentication error: {e}")


# ============================================================================
# REVIEWS API CLIENT
# ============================================================================

class MSStoreReviewsAPI:
    """
    Client for Microsoft Store Analytics API - Reviews endpoint.
    """

    def __init__(self, auth: PartnerCenterAuth, app_id: str):
        self.auth = auth
        self.app_id = app_id
        self.session = requests.Session()

    def _get_headers(self):
        """Get headers with fresh access token"""
        token = self.auth.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get_reviews(self, start_date=None, end_date=None, market=None,
                    rating=None, top=10000, skip=0):
        """
        Retrieve reviews from the Microsoft Store Analytics API.

        Args:
            start_date: Start date for review range (YYYY-MM-DD)
            end_date: End date for review range (YYYY-MM-DD)
            market: Filter by market (e.g., 'US', 'GB', 'DE')
            rating: Filter by rating (1-5)
            top: Max rows to return (max 10000)
            skip: Rows to skip (for pagination)

        Returns:
            dict: API response with reviews
        """
        params = {
            "applicationId": self.app_id,
            "top": min(top, 10000)
        }

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if skip > 0:
            params["skip"] = skip

        # Build filter string
        filters = []
        if market:
            filters.append(f"market eq '{market}'")
        if rating:
            filters.append(f"rating eq {rating}")

        if filters:
            params["filter"] = " and ".join(filters)

        try:
            response = self.session.get(
                ENDPOINTS["reviews"],
                headers=self._get_headers(),
                params=params,
                timeout=60
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = response.json()
            except:
                error_detail = response.text

            raise Exception(f"API request failed: {e}\nDetails: {error_detail}")

    def get_all_reviews(self, start_date=None, end_date=None, market=None,
                        max_reviews=None, progress_callback=None):
        """
        Retrieve all reviews with automatic pagination.

        Args:
            start_date: Start date for review range
            end_date: End date for review range
            market: Filter by market
            max_reviews: Maximum total reviews to retrieve
            progress_callback: Function to call with progress updates

        Returns:
            list: All reviews
        """
        all_reviews = []
        skip = 0
        batch_size = 10000

        while True:
            if progress_callback:
                progress_callback(f"Fetching reviews {skip} to {skip + batch_size}...")

            result = self.get_reviews(
                start_date=start_date,
                end_date=end_date,
                market=market,
                top=batch_size,
                skip=skip
            )

            reviews = result.get("Value", [])
            all_reviews.extend(reviews)

            if progress_callback:
                progress_callback(f"Retrieved {len(all_reviews)} reviews so far...")

            # Check if we should continue
            if len(reviews) < batch_size:
                break  # No more reviews

            if max_reviews and len(all_reviews) >= max_reviews:
                all_reviews = all_reviews[:max_reviews]
                break

            skip += batch_size

        return all_reviews

    def get_reviews_by_market(self, markets, start_date=None, end_date=None):
        """
        Retrieve reviews from multiple markets.

        Args:
            markets: List of market codes (e.g., ['US', 'GB', 'DE'])
            start_date: Start date
            end_date: End date

        Returns:
            dict: Reviews organized by market
        """
        results = {}

        for market in markets:
            print(f"Fetching reviews for {market}...")
            reviews = self.get_all_reviews(
                start_date=start_date,
                end_date=end_date,
                market=market
            )
            results[market] = reviews
            print(f"  Retrieved {len(reviews)} reviews from {market}")

        return results


# ============================================================================
# DATA PROCESSING
# ============================================================================

def normalize_review(review):
    """
    Normalize API review to match iOS scraper format.
    """
    return {
        "id": review.get("id", ""),
        "author": review.get("reviewerName", "Anonymous"),
        "rating": review.get("rating", 0),
        "title": review.get("reviewTitle", ""),
        "content": review.get("reviewText", ""),
        "date": review.get("date", ""),
        "country": review.get("market", ""),
        "version": review.get("packageVersion", ""),
        "device_type": review.get("deviceType", ""),
        "os_version": review.get("osVersion", ""),
        "helpful_count": review.get("helpfulCount", 0),
        "not_helpful_count": review.get("notHelpfulCount", 0),
        "response_date": review.get("responseDate", ""),
        "response_text": review.get("responseText", ""),
        "store": "Microsoft Store"
    }


def analyze_reviews(reviews):
    """Generate analytics from reviews (same format as iOS scraper)"""
    if not reviews:
        return None

    total = len(reviews)
    ratings = [r.get("rating", 0) for r in reviews if r.get("rating", 0) > 0]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    rating_dist = Counter(ratings)
    country_dist = Counter(r.get("country", "unknown") for r in reviews)
    version_dist = Counter(r.get("version", "unknown") for r in reviews)

    return {
        "total_reviews": total,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": dict(sorted(rating_dist.items(), reverse=True)),
        "country_distribution": dict(country_dist.most_common()),
        "version_distribution": dict(version_dist.most_common(10)),
        "store": "Microsoft Store"
    }


# ============================================================================
# FILE EXPORT
# ============================================================================

def save_to_json(data, filename):
    """Save data to JSON file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {filepath}")
    return filepath


def save_to_csv(reviews, filename):
    """Save reviews to CSV file"""
    if not reviews:
        return None

    filepath = os.path.join(OUTPUT_DIR, filename)

    all_keys = set()
    for review in reviews:
        all_keys.update(review.keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(reviews)

    print(f"Saved: {filepath}")
    return filepath


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   MICROSOFT STORE PARTNER CENTER API - REVIEW SCRAPER     ║
    ║                                                           ║
    ║   App: HP Smart                                           ║
    ║   ID:  9wzdncrfhwlh                                       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Check if credentials are configured
    if CONFIG["tenant_id"] == "YOUR_TENANT_ID":
        print("ERROR: Please configure your Azure AD credentials first!")
        print("\nSetup Steps:")
        print("1. Go to Azure Portal (portal.azure.com)")
        print("2. Azure Active Directory > App registrations > New registration")
        print("3. Name your app (e.g., 'MS Store Analytics')")
        print("4. After registration, copy:")
        print("   - Application (client) ID -> CONFIG['client_id']")
        print("   - Directory (tenant) ID -> CONFIG['tenant_id']")
        print("5. Certificates & secrets > New client secret")
        print("   - Copy the secret value -> CONFIG['client_secret']")
        print("6. Associate this app with your Partner Center account:")
        print("   - Go to Partner Center > Account settings > User management")
        print("   - Add the Azure AD app with appropriate permissions")
        print("\nSee: https://learn.microsoft.com/en-us/windows/uwp/monetize/access-analytics-data-using-windows-store-services")
        return

    # Initialize authentication
    print("Authenticating with Azure AD...")
    try:
        auth = PartnerCenterAuth(
            tenant_id=CONFIG["tenant_id"],
            client_id=CONFIG["client_id"],
            client_secret=CONFIG["client_secret"]
        )
        token = auth.get_access_token()
        print("Authentication successful!")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    # Initialize API client
    api = MSStoreReviewsAPI(auth, CONFIG["app_id"])

    # Set date range (last 3 months)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    print(f"\nFetching reviews from {start_date} to {end_date}...")

    # Fetch reviews
    try:
        reviews = api.get_all_reviews(
            start_date=start_date,
            end_date=end_date,
            progress_callback=print
        )
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return

    if not reviews:
        print("No reviews found.")
        return

    # Normalize reviews
    normalized_reviews = [normalize_review(r) for r in reviews]

    # Save data
    print("\nSaving data...")
    save_to_json(normalized_reviews, "MSStore_HP_app_reviews_api.json")
    save_to_csv(normalized_reviews, "MSStore_HP_app_reviews_api.csv")

    # Generate analytics
    analytics = analyze_reviews(normalized_reviews)
    analytics["date_range"] = {"start": start_date, "end": end_date}
    analytics["scrape_date"] = datetime.now().isoformat()
    save_to_json(analytics, "MSStore_HP_app_analytics_api.json")

    # Print summary
    print(f"\n{'='*60}")
    print("SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"\nTotal reviews: {analytics['total_reviews']}")
    print(f"Average rating: {analytics['average_rating']:.2f} / 5.0")
    print("\nRating distribution:")
    for rating in range(5, 0, -1):
        count = analytics['rating_distribution'].get(rating, 0)
        pct = count / analytics['total_reviews'] * 100 if analytics['total_reviews'] > 0 else 0
        print(f"  {rating} stars: {count} ({pct:.1f}%)")


# ============================================================================
# QUICK FUNCTIONS FOR MODULE IMPORT
# ============================================================================

def quick_scrape(tenant_id, client_id, client_secret, app_id,
                 start_date=None, end_date=None, market=None):
    """
    Quick scrape function for importing as module.

    Usage:
        from MSStore_PartnerCenter_API import quick_scrape
        reviews = quick_scrape(
            tenant_id="YOUR_TENANT_ID",
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET",
            app_id="9wzdncrfhwlh",
            start_date="2025-10-01"
        )
    """
    auth = PartnerCenterAuth(tenant_id, client_id, client_secret)
    api = MSStoreReviewsAPI(auth, app_id)

    reviews = api.get_all_reviews(
        start_date=start_date,
        end_date=end_date,
        market=market
    )

    return [normalize_review(r) for r in reviews]


if __name__ == "__main__":
    main()
