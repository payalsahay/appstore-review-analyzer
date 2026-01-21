"""
================================================================================
MSStore_HPApp_scrapper.py
================================================================================

Microsoft Store Review Scraper for HP Smart App

App: HP Smart
App ID: 9wzdncrfhwlh
URL: https://apps.microsoft.com/detail/9wzdncrfhwlh

Author: Payal
Version: 1.0
Created: January 2026

FEATURES:
- Selenium-based scraping (JavaScript rendering required)
- Multi-market support (US, GB, CA, AU, DE, FR, etc.)
- Export to CSV and JSON (same format as iOS scraper)
- Basic analytics
- Rate limiting to avoid blocks

REQUIREMENTS:
    pip install selenium webdriver-manager

USAGE:
    python MSStore_HPApp_scrapper.py

OUTPUT:
    - MSStore_HP_app_reviews.csv
    - MSStore_HP_app_reviews.json

================================================================================
"""

import json
import csv
import time
import os
from datetime import datetime
from collections import Counter

# ============================================================================
# HP APP CONFIGURATION (Microsoft Store)
# ============================================================================

APP_CONFIG = {
    "app_id": "9wzdncrfhwlh",
    "app_name": "HP Smart",
    "display_name": "HP Smart (Microsoft Store)",
    "publisher": "HP Inc.",
    "store_url": "https://apps.microsoft.com/detail/9wzdncrfhwlh"
}

# Markets to scrape (language-country codes)
MARKETS = [
    ("en-us", "US"),   # United States
    ("en-gb", "GB"),   # United Kingdom
    ("en-ca", "CA"),   # Canada
    ("en-au", "AU"),   # Australia
    ("de-de", "DE"),   # Germany
    ("fr-fr", "FR"),   # France
    ("es-es", "ES"),   # Spain
    ("it-it", "IT"),   # Italy
    ("pt-br", "BR"),   # Brazil
    ("ja-jp", "JP"),   # Japan
]

# Rate limiting
REQUEST_DELAY = 2  # seconds between page loads
MAX_REVIEWS_PER_MARKET = 100  # Microsoft Store shows limited reviews

# Output directory
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================================
# SELENIUM SCRAPER
# ============================================================================

class MSStoreScraper:
    """
    Scrapes Microsoft Store reviews using Selenium.
    Requires Chrome/Chromium browser and chromedriver.
    """

    def __init__(self, app_id, headless=True):
        self.app_id = app_id
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initialize Selenium WebDriver - tries Chrome first, then Safari"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Store imports for later use
            self.By = By
            self.WebDriverWait = WebDriverWait
            self.EC = EC

            # Try Chrome first
            try:
                from selenium.webdriver.chrome.service import Service
                from selenium.webdriver.chrome.options import Options

                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                except ImportError:
                    service = Service()

                options = Options()
                if self.headless:
                    options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.implicitly_wait(10)
                print("    Using Chrome WebDriver")
                return True

            except Exception as chrome_error:
                print(f"    Chrome not available: {str(chrome_error)[:50]}...")

                # Try Safari (macOS only)
                try:
                    print("    Trying Safari WebDriver...")
                    from selenium.webdriver.safari.options import Options as SafariOptions

                    safari_options = SafariOptions()
                    self.driver = webdriver.Safari(options=safari_options)
                    self.driver.implicitly_wait(10)
                    print("    Using Safari WebDriver")
                    return True

                except Exception as safari_error:
                    print(f"    Safari not available: {str(safari_error)[:50]}...")

                    # Try Firefox as last resort
                    try:
                        print("    Trying Firefox WebDriver...")
                        from selenium.webdriver.firefox.options import Options as FirefoxOptions

                        firefox_options = FirefoxOptions()
                        if self.headless:
                            firefox_options.add_argument("--headless")

                        self.driver = webdriver.Firefox(options=firefox_options)
                        self.driver.implicitly_wait(10)
                        print("    Using Firefox WebDriver")
                        return True

                    except Exception as firefox_error:
                        print(f"    Firefox not available: {str(firefox_error)[:50]}...")
                        raise Exception("No supported browser found. Install Chrome, Firefox, or enable Safari WebDriver.")

        except ImportError as e:
            print(f"\nError: Selenium not installed.")
            print("Install with: pip install selenium webdriver-manager")
            return False
        except Exception as e:
            print(f"\nError initializing WebDriver: {e}")
            print("\nTo fix this, either:")
            print("  1. Install Chrome: https://www.google.com/chrome/")
            print("  2. Enable Safari WebDriver: safaridriver --enable (in Terminal)")
            print("  3. Install Firefox: https://www.mozilla.org/firefox/")
            return False

    def _close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_app_info(self, locale="en-us"):
        """Get basic app information"""
        url = f"https://apps.microsoft.com/detail/{self.app_id}?hl={locale}"

        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for page load

            info = {
                "app_id": self.app_id,
                "url": url,
                "locale": locale
            }

            # Try to extract rating
            try:
                rating_elem = self.driver.find_element(self.By.CSS_SELECTOR, "[class*='rating']")
                info["rating_text"] = rating_elem.text
            except:
                pass

            # Try to extract title
            try:
                title_elem = self.driver.find_element(self.By.TAG_NAME, "h1")
                info["title"] = title_elem.text
            except:
                pass

            return info

        except Exception as e:
            print(f"Error getting app info: {e}")
            return None

    def scrape_reviews(self, locale="en-us", country="US", max_reviews=50):
        """Scrape reviews for a specific market"""
        url = f"https://apps.microsoft.com/detail/{self.app_id}?hl={locale}"
        reviews = []

        try:
            print(f"    Loading page: {url[:60]}...")
            self.driver.get(url)
            time.sleep(3)

            # Scroll to reviews section
            try:
                # Find and click on reviews tab/section
                review_section = self.driver.find_element(
                    self.By.XPATH,
                    "//*[contains(text(), 'Ratings and reviews') or contains(text(), 'Reviews')]"
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", review_section)
                time.sleep(2)

                # Try clicking to expand reviews
                try:
                    review_section.click()
                    time.sleep(2)
                except:
                    pass

            except Exception as e:
                print(f"    Could not find reviews section: {e}")

            # Try multiple selectors to find reviews
            review_selectors = [
                "[class*='review-card']",
                "[class*='ReviewCard']",
                "[class*='review-item']",
                "[class*='user-review']",
                "[data-testid*='review']",
                ".review",
                "[class*='Rating'] + div",  # Rating followed by review content
            ]

            review_elements = []
            for selector in review_selectors:
                try:
                    elements = self.driver.find_elements(self.By.CSS_SELECTOR, selector)
                    if elements:
                        review_elements = elements
                        print(f"    Found {len(elements)} review elements with selector: {selector}")
                        break
                except:
                    continue

            # If no review cards found, try to extract from page source
            if not review_elements:
                print("    No review cards found. Checking page source...")
                page_source = self.driver.page_source

                # Look for JSON-LD data
                try:
                    import re
                    json_ld_match = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                                             page_source, re.DOTALL)
                    if json_ld_match:
                        ld_data = json.loads(json_ld_match.group(1))
                        if 'aggregateRating' in ld_data:
                            print(f"    Found aggregate rating: {ld_data['aggregateRating']}")
                except:
                    pass

            # Extract data from review elements
            for i, elem in enumerate(review_elements[:max_reviews]):
                try:
                    review_data = self._extract_review_data(elem, country)
                    if review_data:
                        reviews.append(review_data)
                except Exception as e:
                    print(f"    Error extracting review {i}: {e}")

            # Try to load more reviews by scrolling
            if len(reviews) < max_reviews:
                print("    Scrolling to load more reviews...")
                last_count = len(reviews)
                scroll_attempts = 0

                while len(reviews) < max_reviews and scroll_attempts < 5:
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(1)

                    # Re-check for reviews
                    for selector in review_selectors:
                        try:
                            elements = self.driver.find_elements(self.By.CSS_SELECTOR, selector)
                            for elem in elements[len(reviews):max_reviews]:
                                review_data = self._extract_review_data(elem, country)
                                if review_data and review_data not in reviews:
                                    reviews.append(review_data)
                            break
                        except:
                            continue

                    if len(reviews) == last_count:
                        scroll_attempts += 1
                    else:
                        last_count = len(reviews)
                        scroll_attempts = 0

            return reviews

        except Exception as e:
            print(f"    Error scraping reviews: {e}")
            return reviews

    def _extract_review_data(self, element, country):
        """Extract review data from a review element"""
        try:
            review = {
                "id": "",
                "author": "Anonymous",
                "rating": 0,
                "title": "",
                "content": "",
                "date": "",
                "country": country,
                "helpful_count": 0,
                "version": "",
                "store": "Microsoft Store"
            }

            # Try various selectors for each field
            text = element.text

            # Extract rating (look for star patterns)
            try:
                rating_elem = element.find_element(self.By.CSS_SELECTOR, "[class*='star'], [class*='rating'], [aria-label*='star']")
                rating_text = rating_elem.get_attribute("aria-label") or rating_elem.text
                import re
                rating_match = re.search(r'(\d+)', rating_text)
                if rating_match:
                    review["rating"] = int(rating_match.group(1))
            except:
                # Try to infer from filled stars
                try:
                    stars = element.find_elements(self.By.CSS_SELECTOR, "[class*='filled'], [class*='active']")
                    if stars:
                        review["rating"] = len(stars)
                except:
                    pass

            # Extract author
            try:
                author_elem = element.find_element(self.By.CSS_SELECTOR, "[class*='author'], [class*='user'], [class*='name']")
                review["author"] = author_elem.text.strip()
            except:
                pass

            # Extract title
            try:
                title_elem = element.find_element(self.By.CSS_SELECTOR, "[class*='title'], h3, h4, strong")
                review["title"] = title_elem.text.strip()
            except:
                pass

            # Extract content
            try:
                content_elem = element.find_element(self.By.CSS_SELECTOR, "[class*='content'], [class*='text'], [class*='body'], p")
                review["content"] = content_elem.text.strip()
            except:
                # Use full text if no specific content found
                if text and len(text) > 10:
                    review["content"] = text[:500]

            # Extract date
            try:
                date_elem = element.find_element(self.By.CSS_SELECTOR, "[class*='date'], time, [datetime]")
                review["date"] = date_elem.get_attribute("datetime") or date_elem.text
            except:
                pass

            # Only return if we have meaningful content
            if review["content"] or review["rating"] > 0:
                return review
            return None

        except Exception as e:
            return None

    def scrape_all_markets(self, markets=None, max_reviews_per_market=50):
        """Scrape reviews from multiple markets"""
        if markets is None:
            markets = MARKETS

        all_reviews = []
        market_stats = {}

        print(f"\n{'='*60}")
        print(f"MS STORE REVIEW SCRAPER")
        print(f"App: {APP_CONFIG['display_name']} (ID: {self.app_id})")
        print(f"{'='*60}\n")

        # Initialize driver
        if not self._init_driver():
            return [], {}

        try:
            for i, (locale, country) in enumerate(markets, 1):
                print(f"[{i}/{len(markets)}] Scraping {country} ({locale})...")

                reviews = self.scrape_reviews(locale, country, max_reviews_per_market)
                market_stats[country] = len(reviews)
                all_reviews.extend(reviews)

                print(f"    Collected: {len(reviews)} reviews\n")
                time.sleep(REQUEST_DELAY)

        finally:
            self._close_driver()

        print(f"{'='*60}")
        print(f"SCRAPING COMPLETE")
        print(f"Total reviews: {len(all_reviews)}")
        print(f"{'='*60}\n")

        return all_reviews, market_stats


# ============================================================================
# ALTERNATIVE: API-BASED SCRAPER (if available)
# ============================================================================

class MSStoreAPIScraper:
    """
    Attempts to scrape Microsoft Store using discovered API endpoints.
    This is a fallback method that may not return full review data.
    """

    def __init__(self, app_id):
        self.app_id = app_id
        self.session = None

    def _init_session(self):
        """Initialize requests session"""
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def get_app_rating(self, market="US"):
        """Get aggregate rating for the app"""
        if not self.session:
            self._init_session()

        url = f"https://apps.microsoft.com/detail/{self.app_id}?gl={market}"

        try:
            response = self.session.get(url, timeout=30)

            # Extract rating from page
            import re

            # Look for aggregateRating in JSON-LD
            ld_match = re.search(r'"aggregateRating":\s*\{[^}]+\}', response.text)
            if ld_match:
                rating_json = "{" + ld_match.group(0) + "}"
                rating_data = json.loads(rating_json)
                return rating_data.get("aggregateRating", {})

            # Look for rating value directly
            rating_match = re.search(r'"ratingValue":\s*([\d.]+)', response.text)
            count_match = re.search(r'"ratingCount":\s*(\d+)', response.text)

            if rating_match:
                return {
                    "ratingValue": float(rating_match.group(1)),
                    "ratingCount": int(count_match.group(1)) if count_match else 0
                }

            return None

        except Exception as e:
            print(f"Error getting app rating: {e}")
            return None


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

    # Get all unique keys
    all_keys = set()
    for review in reviews:
        all_keys.update(review.keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(reviews)

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
    ratings = [r.get("rating", 0) for r in reviews if r.get("rating", 0) > 0]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    rating_dist = Counter(ratings)
    country_dist = Counter(r.get("country", "unknown") for r in reviews)

    return {
        "total_reviews": total,
        "reviews_with_rating": len(ratings),
        "average_rating": round(avg_rating, 2),
        "rating_distribution": dict(sorted(rating_dist.items(), reverse=True)),
        "country_distribution": dict(country_dist.most_common()),
        "store": "Microsoft Store"
    }


def print_analytics(analytics, market_stats):
    """Print analytics to console"""
    print(f"\n{'='*60}")
    print("ANALYTICS SUMMARY")
    print(f"{'='*60}")

    print(f"\nTotal Reviews: {analytics['total_reviews']}")
    print(f"Reviews with Rating: {analytics['reviews_with_rating']}")
    print(f"Average Rating: {analytics['average_rating']:.2f} / 5.0")

    if analytics["rating_distribution"]:
        print("\nRating Distribution:")
        total = analytics["reviews_with_rating"]
        for rating in range(5, 0, -1):
            count = analytics["rating_distribution"].get(rating, 0)
            pct = count / total * 100 if total > 0 else 0
            bar = "█" * int(pct / 2)
            print(f"  {rating} stars: {count:5d} ({pct:5.1f}%) {bar}")

    print("\nReviews by Market:")
    for country, count in list(analytics["country_distribution"].items())[:10]:
        print(f"  {country}: {count}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║       MICROSOFT STORE REVIEW SCRAPER                      ║
    ║                                                           ║
    ║   App: HP Smart                                           ║
    ║   ID:  9wzdncrfhwlh                                       ║
    ║   URL: apps.microsoft.com/detail/9wzdncrfhwlh             ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Check for Selenium
    try:
        from selenium import webdriver
        selenium_available = True
    except ImportError:
        selenium_available = False
        print("WARNING: Selenium not installed.")
        print("Install with: pip install selenium webdriver-manager\n")

    # First, get aggregate rating via API
    print("Getting aggregate app rating...")
    api_scraper = MSStoreAPIScraper(APP_CONFIG["app_id"])
    rating_info = api_scraper.get_app_rating("US")

    if rating_info:
        print(f"\nMS Store Aggregate Rating:")
        print(f"  Rating: {rating_info.get('ratingValue', 'N/A')} / 5.0")
        print(f"  Total Ratings: {rating_info.get('ratingCount', 'N/A'):,}")

    if not selenium_available:
        print("\nTo scrape individual reviews, please install Selenium:")
        print("  pip install selenium webdriver-manager")
        print("\nThen run this script again.")
        return

    # Run Selenium scraper
    print("\n" + "="*60)
    print("Starting review scraper (this may take a few minutes)...")
    print("="*60)

    scraper = MSStoreScraper(APP_CONFIG["app_id"], headless=True)
    reviews, market_stats = scraper.scrape_all_markets(
        markets=MARKETS[:5],  # Start with 5 markets
        max_reviews_per_market=50
    )

    if not reviews:
        print("\nNo reviews collected. Microsoft Store may have changed their page structure.")
        print("Try running with headless=False to debug.")
        return

    # Save data
    print("\nSaving data...")
    save_to_json(reviews, "MSStore_HP_app_reviews.json")
    save_to_csv(reviews, "MSStore_HP_app_reviews.csv")

    # Analytics
    analytics = analyze_reviews(reviews)
    if analytics:
        print_analytics(analytics, market_stats)

        analytics["market_stats"] = market_stats
        analytics["scrape_date"] = datetime.now().isoformat()
        analytics["app_config"] = APP_CONFIG
        if rating_info:
            analytics["store_aggregate_rating"] = rating_info
        save_to_json(analytics, "MSStore_HP_app_analytics.json")

    print(f"\n{'='*60}")
    print("SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"\nFiles saved to: {OUTPUT_DIR}")
    print("  - MSStore_HP_app_reviews.json")
    print("  - MSStore_HP_app_reviews.csv")
    print("  - MSStore_HP_app_analytics.json")
    print()


# ============================================================================
# QUICK RUN FUNCTIONS (For importing as module)
# ============================================================================

def quick_scrape(markets=None, max_reviews=50):
    """
    Quick scrape function for importing as module.

    Usage:
        from MSStore_HPApp_scrapper import quick_scrape
        reviews = quick_scrape(markets=[("en-us", "US")], max_reviews=50)
    """
    if markets is None:
        markets = [("en-us", "US")]

    scraper = MSStoreScraper(APP_CONFIG["app_id"], headless=True)
    reviews, _ = scraper.scrape_all_markets(markets, max_reviews)

    return reviews


def get_store_rating():
    """
    Get the aggregate store rating (no Selenium required).

    Usage:
        from MSStore_HPApp_scrapper import get_store_rating
        rating = get_store_rating()
    """
    api_scraper = MSStoreAPIScraper(APP_CONFIG["app_id"])
    return api_scraper.get_app_rating("US")


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
