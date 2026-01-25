"""
================================================================================
Weekly Friday Scraper - Automated Review Collection & Analysis
================================================================================

Runs every Friday at 8AM PST via GitHub Actions.

COLLECTS:
1. iOS US - Last 30 days rolling
2. iOS All Countries - Last 30 days rolling
3. iOS US - Last 500 reviews
4. Android US - Last 30 days rolling
5. Android All Countries - Last 30 days rolling
6. Android US - Last 500 reviews
7. Combined iOS + Android US

FEATURES:
- Deduplication: Appends new reviews, removes duplicates by review ID
- Rolling window: Keeps only reviews within date range for 30-day data
- Runs CustomerInsight_Review_Agent for analysis
- Commits all changes to GitHub

Author: Payal
Version: 1.1
Created: January 2026

================================================================================
"""

import json
import csv
import os
import sys
from datetime import datetime, timedelta
from collections import Counter

# Optional: matplotlib for chart generation
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_CONFIG = {
    "ios": {
        "app_id": 469284907,
        "app_name": "hp-smart",
        "display_name": "HP App",
    },
    "android": {
        "package_id": "com.hp.printercontrol",
        "app_name": "HP Smart",
        "display_name": "HP App",
    }
}

# Countries for multi-country scraping
ALL_COUNTRIES = [
    "us", "gb", "ca", "au", "in", "de", "fr", "jp", "br", "mx",
    "es", "it", "nl", "se", "sg"
]

# Language mapping for Google Play
COUNTRY_LANGUAGE_MAP = {
    "us": "en", "gb": "en", "ca": "en", "au": "en", "in": "en",
    "de": "de", "fr": "fr", "jp": "ja", "br": "pt", "mx": "es",
    "es": "es", "it": "it", "nl": "nl", "se": "sv", "sg": "en",
}

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
IOS_DATA_DIR = os.path.join(DATA_DIR, "ios")
ANDROID_DATA_DIR = os.path.join(DATA_DIR, "googleplay")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
INSIGHTS_DIR = os.path.join(OUTPUT_DIR, "insights")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

# Historical rating data file
RATING_HISTORY_FILE = os.path.join(DATA_DIR, "app_rating_history.json")

# Visualizations directory
VISUALIZATIONS_DIR = os.path.join(OUTPUT_DIR, "visualizations")

# Ensure directories exist
for d in [IOS_DATA_DIR, ANDROID_DATA_DIR, INSIGHTS_DIR, REPORTS_DIR, VISUALIZATIONS_DIR]:
    os.makedirs(d, exist_ok=True)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_existing_reviews(filepath):
    """Load existing reviews from JSON file"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_reviews(reviews, filepath):
    """Save reviews to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved {len(reviews)} reviews to {os.path.basename(filepath)}")


def save_to_csv(reviews, filepath):
    """Save reviews to CSV file"""
    if not reviews:
        return

    fieldnames = ["id", "author", "rating", "title", "content", "version",
                  "date", "country", "platform", "vote_count"]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(reviews)
    print(f"  Saved CSV to {os.path.basename(filepath)}")


def deduplicate_reviews(existing, new_reviews):
    """
    Merge reviews: add new, keep unique by ID.
    Returns deduplicated list sorted by date (newest first).
    """
    reviews_by_id = {}

    # Add existing reviews
    for review in existing:
        review_id = str(review.get('id', ''))
        if review_id:
            reviews_by_id[review_id] = review

    # Add/update with new reviews
    added_count = 0
    for review in new_reviews:
        review_id = str(review.get('id', ''))
        if review_id and review_id not in reviews_by_id:
            added_count += 1
        if review_id:
            reviews_by_id[review_id] = review

    # Sort by date (newest first)
    all_reviews = list(reviews_by_id.values())
    all_reviews.sort(key=lambda x: x.get('date', ''), reverse=True)

    print(f"  Added {added_count} new reviews, total: {len(all_reviews)}")
    return all_reviews


def filter_reviews_by_date(reviews, days_back):
    """Filter reviews to only include those within the date range"""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    filtered = []

    for review in reviews:
        date_str = review.get('date', '')
        if date_str:
            try:
                # Handle various date formats
                if 'T' in date_str:
                    review_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    if review_date.tzinfo:
                        review_date = review_date.replace(tzinfo=None)
                else:
                    review_date = datetime.strptime(date_str[:10], '%Y-%m-%d')

                if review_date >= cutoff_date:
                    filtered.append(review)
            except (ValueError, TypeError):
                # Keep reviews with unparseable dates
                filtered.append(review)

    print(f"  Filtered to {len(filtered)} reviews (last {days_back} days)")
    return filtered


def generate_analytics(reviews, platform, country, days=None):
    """Generate analytics summary"""
    if not reviews:
        return None

    total = len(reviews)
    ratings = [r.get('rating', 0) for r in reviews if r.get('rating')]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    rating_dist = Counter(ratings)
    version_dist = Counter(r.get('version', 'unknown') for r in reviews if r.get('version'))

    dates = [r.get('date', '')[:10] for r in reviews if r.get('date')]

    analytics = {
        "scrape_date": datetime.now().isoformat(),
        "total_reviews": total,
        "avg_rating": round(avg_rating, 2),
        "rating_distribution": dict(sorted(rating_dist.items(), reverse=True)),
        "version_distribution": dict(version_dist.most_common(10)),
        "one_star_count": rating_dist.get(1, 0),
        "one_star_pct": round(rating_dist.get(1, 0) / total * 100, 1) if total > 0 else 0,
        "five_star_count": rating_dist.get(5, 0),
        "five_star_pct": round(rating_dist.get(5, 0) / total * 100, 1) if total > 0 else 0,
        "platform": platform,
        "country": country,
        "date_range": {
            "from": min(dates) if dates else None,
            "to": max(dates) if dates else None,
        }
    }

    if days:
        analytics["days"] = days

    return analytics


# ============================================================================
# APP STORE RATING FETCHERS
# ============================================================================

def fetch_ios_app_rating(country="us"):
    """
    Fetch the current iOS App Store rating for the app using iTunes API.
    Returns dict with rating info or None on error.
    """
    print(f"  Fetching iOS App Store rating for {country.upper()}...")

    import urllib.request
    import urllib.error

    app_id = APP_CONFIG["ios"]["app_id"]
    url = f"https://itunes.apple.com/lookup?id={app_id}&country={country}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get('resultCount', 0) > 0:
            app_info = data['results'][0]

            rating_info = {
                "rating": app_info.get('averageUserRating'),
                "rating_count": app_info.get('userRatingCount'),
                "current_version_rating": app_info.get('averageUserRatingForCurrentVersion'),
                "current_version_rating_count": app_info.get('userRatingCountForCurrentVersion'),
                "version": app_info.get('version'),
                "app_name": app_info.get('trackName'),
            }

            print(f"  iOS {country.upper()} rating: {rating_info.get('rating', 'N/A')}")
            return rating_info
        else:
            print(f"  No iOS app found for ID {app_id}")
            return None

    except urllib.error.URLError as e:
        print(f"  Error fetching iOS rating for {country}: {e}")
        return None
    except Exception as e:
        print(f"  Error fetching iOS rating for {country}: {e}")
        return None


def fetch_android_app_rating(country="us"):
    """
    Fetch the current Google Play Store rating for the app.
    Returns dict with rating info or None on error.
    """
    print(f"  Fetching Android Play Store rating for {country.upper()}...")

    try:
        from google_play_scraper import app as get_app_details
    except ImportError:
        print("  ERROR: google-play-scraper not installed")
        return None

    lang = COUNTRY_LANGUAGE_MAP.get(country, "en")

    try:
        app_details = get_app_details(
            APP_CONFIG["android"]["package_id"],
            lang=lang,
            country=country
        )

        rating_info = {
            "rating": app_details.get('score'),
            "rating_count": app_details.get('ratings'),
            "installs": app_details.get('installs'),
            "reviews_count": app_details.get('reviews'),
            "histogram": app_details.get('histogram'),  # [1-star, 2-star, 3-star, 4-star, 5-star counts]
        }

        print(f"  Android {country.upper()} rating: {rating_info.get('rating', 'N/A')}")
        return rating_info

    except Exception as e:
        print(f"  Error fetching Android rating for {country}: {e}")
        return None


def load_rating_history():
    """Load existing rating history from file"""
    if os.path.exists(RATING_HISTORY_FILE):
        try:
            with open(RATING_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"ios": [], "android": []}
    return {"ios": [], "android": []}


def save_rating_history(history):
    """Save rating history to file"""
    with open(RATING_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved rating history to {os.path.basename(RATING_HISTORY_FILE)}")


def record_app_ratings():
    """
    Fetch current app ratings for iOS and Android and append to history.
    Returns the current ratings dict.
    """
    print("\n  Recording App Store Ratings...")

    timestamp = datetime.now().isoformat()
    date_str = datetime.now().strftime('%Y-%m-%d')

    # Fetch ratings for key countries
    ios_us_rating = fetch_ios_app_rating("us")
    android_us_rating = fetch_android_app_rating("us")

    # Load existing history
    history = load_rating_history()

    # Create today's record
    current_ratings = {
        "date": date_str,
        "timestamp": timestamp,
        "ios": {
            "us": ios_us_rating
        },
        "android": {
            "us": android_us_rating
        }
    }

    # Append iOS history entry
    if ios_us_rating and ios_us_rating.get("rating"):
        ios_entry = {
            "date": date_str,
            "timestamp": timestamp,
            "country": "us",
            "rating": ios_us_rating.get("rating"),
            "rating_count": ios_us_rating.get("rating_count"),
            "current_version_rating": ios_us_rating.get("current_version_rating"),
        }
        history["ios"].append(ios_entry)

    # Append Android history entry
    if android_us_rating and android_us_rating.get("rating"):
        android_entry = {
            "date": date_str,
            "timestamp": timestamp,
            "country": "us",
            "rating": android_us_rating.get("rating"),
            "rating_count": android_us_rating.get("rating_count"),
            "installs": android_us_rating.get("installs"),
            "histogram": android_us_rating.get("histogram"),
        }
        history["android"].append(android_entry)

    # Save updated history
    save_rating_history(history)

    # Also save a current snapshot for easy access
    current_ratings_file = os.path.join(DATA_DIR, "current_app_ratings.json")
    with open(current_ratings_file, 'w', encoding='utf-8') as f:
        json.dump(current_ratings, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved current ratings to current_app_ratings.json")

    return current_ratings


def get_rating_trend(platform, days=30):
    """
    Get rating trend for the specified platform over the last N days.
    Returns dict with trend analysis.
    """
    history = load_rating_history()
    entries = history.get(platform, [])

    if not entries:
        return None

    # Filter to last N days
    cutoff = datetime.now() - timedelta(days=days)
    recent_entries = []
    for entry in entries:
        try:
            entry_date = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
            if entry_date >= cutoff:
                recent_entries.append(entry)
        except (ValueError, TypeError):
            continue

    if not recent_entries:
        return None

    # Calculate trend
    ratings = [e.get('rating') for e in recent_entries if e.get('rating')]
    if len(ratings) < 2:
        return {
            "current": ratings[-1] if ratings else None,
            "entries": len(recent_entries),
            "trend": "insufficient_data"
        }

    oldest_rating = ratings[0]
    newest_rating = ratings[-1]
    change = newest_rating - oldest_rating

    if change > 0.1:
        trend = "improving"
    elif change < -0.1:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "current": newest_rating,
        "oldest": oldest_rating,
        "change": round(change, 2),
        "trend": trend,
        "entries": len(recent_entries),
        "avg_rating": round(sum(ratings) / len(ratings), 2),
        "min_rating": min(ratings),
        "max_rating": max(ratings),
    }


def generate_rating_history_chart(days=30):
    """
    Generate a line chart showing iOS and Android rating history for the last N days.
    Returns the path to the saved chart image, or None if chart couldn't be generated.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("  Warning: matplotlib not available, skipping chart generation")
        return None

    history = load_rating_history()

    # Get data for both platforms
    cutoff = datetime.now() - timedelta(days=days)

    ios_dates = []
    ios_ratings = []
    android_dates = []
    android_ratings = []

    # Process iOS history (use timestamp for finer granularity)
    for entry in history.get("ios", []):
        try:
            timestamp_str = entry.get('timestamp', '')
            if timestamp_str:
                entry_datetime = datetime.fromisoformat(timestamp_str)
            else:
                entry_datetime = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
            if entry_datetime >= cutoff and entry.get('rating'):
                ios_dates.append(entry_datetime)
                ios_ratings.append(entry['rating'])
        except (ValueError, TypeError):
            continue

    # Process Android history (use timestamp for finer granularity)
    for entry in history.get("android", []):
        try:
            timestamp_str = entry.get('timestamp', '')
            if timestamp_str:
                entry_datetime = datetime.fromisoformat(timestamp_str)
            else:
                entry_datetime = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
            if entry_datetime >= cutoff and entry.get('rating'):
                android_dates.append(entry_datetime)
                android_ratings.append(entry['rating'])
        except (ValueError, TypeError):
            continue

    # Check if we have any data to plot
    if not ios_dates and not android_dates:
        print("  No rating history data available for chart")
        return None

    # Create the chart
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot iOS ratings
    if ios_dates:
        ax.plot(ios_dates, ios_ratings, '-o', label='iOS App Store',
                linewidth=2, markersize=8, color='#007AFF')
        # Add data labels for iOS
        for i, (date, rating) in enumerate(zip(ios_dates, ios_ratings)):
            ax.annotate(f'{rating:.2f}', (date, rating),
                       textcoords="offset points", xytext=(0, 10),
                       ha='center', fontsize=9, color='#007AFF')

    # Plot Android ratings
    if android_dates:
        ax.plot(android_dates, android_ratings, '-s', label='Google Play',
                linewidth=2, markersize=8, color='#34A853')
        # Add data labels for Android
        for i, (date, rating) in enumerate(zip(android_dates, android_ratings)):
            ax.annotate(f'{rating:.2f}', (date, rating),
                       textcoords="offset points", xytext=(0, -15),
                       ha='center', fontsize=9, color='#34A853')

    # Customize the chart
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Rating (out of 5.0)', fontsize=12)
    ax.set_title(f'App Store Ratings - Last {days} Days', fontsize=14, fontweight='bold')

    # Set y-axis limits (ratings are 1-5)
    ax.set_ylim(3.5, 5.0)

    # Format x-axis dates
    all_dates = ios_dates + android_dates
    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
        date_range = (max_date - min_date).days

        # Set x-axis limits with padding
        if date_range == 0:
            # Single day of data - show a week range centered on that date
            ax.set_xlim(min_date - timedelta(days=3), max_date + timedelta(days=3))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        elif date_range <= 7:
            ax.set_xlim(min_date - timedelta(days=1), max_date + timedelta(days=1))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        elif date_range <= 30:
            ax.set_xlim(min_date - timedelta(days=1), max_date + timedelta(days=1))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, date_range // 7)))
        else:
            ax.set_xlim(min_date - timedelta(days=1), max_date + timedelta(days=1))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

    # Use datetime format that shows time if data spans less than 2 days
    if all_dates and date_range <= 1:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))
    else:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45, ha='right')

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)

    # Add legend
    ax.legend(loc='lower right', fontsize=10)

    # Add horizontal reference lines
    ax.axhline(y=4.5, color='gray', linestyle=':', alpha=0.5, label='4.5 reference')
    ax.axhline(y=4.0, color='gray', linestyle=':', alpha=0.5, label='4.0 reference')

    # Tight layout
    plt.tight_layout()

    # Save the chart
    chart_path = os.path.join(VISUALIZATIONS_DIR, f"rating_history_{days}d.png")
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"  Generated rating history chart: {os.path.basename(chart_path)}")
    return chart_path


def generate_rating_history_json():
    """
    Generate a JSON file with rating history data and trends for both platforms.
    Returns the path to the saved JSON file.
    """
    history = load_rating_history()
    ios_trend_30d = get_rating_trend("ios", days=30)
    ios_trend_90d = get_rating_trend("ios", days=90)
    android_trend_30d = get_rating_trend("android", days=30)
    android_trend_90d = get_rating_trend("android", days=90)

    # Get current ratings
    current_ratings = {}
    current_ratings_file = os.path.join(DATA_DIR, "current_app_ratings.json")
    if os.path.exists(current_ratings_file):
        try:
            with open(current_ratings_file, 'r') as f:
                current_ratings = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Build the JSON report
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "generated_date": datetime.now().strftime('%Y-%m-%d'),
        "summary": {
            "ios": {
                "current_rating": current_ratings.get("ios", {}).get("us", {}).get("rating"),
                "rating_count": current_ratings.get("ios", {}).get("us", {}).get("rating_count"),
                "current_version": current_ratings.get("ios", {}).get("us", {}).get("version"),
                "current_version_rating": current_ratings.get("ios", {}).get("us", {}).get("current_version_rating"),
            },
            "android": {
                "current_rating": current_ratings.get("android", {}).get("us", {}).get("rating"),
                "rating_count": current_ratings.get("android", {}).get("us", {}).get("rating_count"),
                "installs": current_ratings.get("android", {}).get("us", {}).get("installs"),
                "histogram": current_ratings.get("android", {}).get("us", {}).get("histogram"),
            }
        },
        "trends": {
            "ios": {
                "30_day": ios_trend_30d,
                "90_day": ios_trend_90d,
            },
            "android": {
                "30_day": android_trend_30d,
                "90_day": android_trend_90d,
            }
        },
        "history": {
            "ios": history.get("ios", []),
            "android": history.get("android", []),
        },
        "data_points": {
            "ios_count": len(history.get("ios", [])),
            "android_count": len(history.get("android", [])),
        }
    }

    # Save the JSON report
    json_path = os.path.join(REPORTS_DIR, "rating_history_report.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)

    print(f"  Generated rating history JSON: {os.path.basename(json_path)}")
    return json_path


def generate_rating_history_report():
    """
    Generate a markdown report showing rating history and trends for both platforms.
    """
    history = load_rating_history()
    ios_trend = get_rating_trend("ios", days=90)
    android_trend = get_rating_trend("android", days=90)

    # Generate the 30-day rating history chart
    chart_path = generate_rating_history_chart(days=30)
    chart_section = ""
    if chart_path:
        # Use relative path for markdown
        rel_chart_path = os.path.relpath(chart_path, INSIGHTS_DIR)
        chart_section = f"""
---

## 30-Day Rating Trend Chart

![Rating History Chart]({rel_chart_path})

"""

    report = f"""# App Rating History Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Current Ratings Overview

| Platform | Current Rating | 90-Day Trend | Change |
|----------|---------------|--------------|--------|
"""

    # iOS row
    if ios_trend and ios_trend.get("current"):
        trend_indicator = ""
        if ios_trend["trend"] == "improving":
            trend_indicator = "Improving"
        elif ios_trend["trend"] == "declining":
            trend_indicator = "Declining"
        else:
            trend_indicator = "Stable"
        change = ios_trend.get("change", 0)
        report += f"| iOS App Store | {ios_trend['current']:.2f} | {trend_indicator} | {change:+.2f} |\n"
    else:
        report += "| iOS App Store | N/A | N/A | N/A |\n"

    # Android row
    if android_trend and android_trend.get("current"):
        trend_indicator = ""
        if android_trend["trend"] == "improving":
            trend_indicator = "Improving"
        elif android_trend["trend"] == "declining":
            trend_indicator = "Declining"
        else:
            trend_indicator = "Stable"
        change = android_trend.get("change", 0)
        report += f"| Google Play | {android_trend['current']:.2f} | {trend_indicator} | {change:+.2f} |\n"
    else:
        report += "| Google Play | N/A | N/A | N/A |\n"

    # Add chart section if available
    if chart_section:
        report += chart_section

    # iOS History Section
    report += """
---

## iOS App Store Rating History

| Date | Rating | Rating Count |
|------|--------|--------------|
"""
    ios_entries = history.get("ios", [])[-20:]  # Last 20 entries
    for entry in reversed(ios_entries):
        date = entry.get("date", "N/A")
        rating = entry.get("rating", "N/A")
        rating_count = entry.get("rating_count", "N/A")
        if rating != "N/A":
            rating = f"{rating:.2f}"
        if rating_count != "N/A" and isinstance(rating_count, (int, float)):
            rating_count = f"{rating_count:,}"
        report += f"| {date} | {rating} | {rating_count} |\n"

    # Android History Section
    report += """
---

## Google Play Store Rating History

| Date | Rating | Rating Count | Installs |
|------|--------|--------------|----------|
"""
    android_entries = history.get("android", [])[-20:]  # Last 20 entries
    for entry in reversed(android_entries):
        date = entry.get("date", "N/A")
        rating = entry.get("rating", "N/A")
        rating_count = entry.get("rating_count", "N/A")
        installs = entry.get("installs", "N/A")
        if rating != "N/A":
            rating = f"{rating:.2f}"
        if rating_count != "N/A" and isinstance(rating_count, (int, float)):
            rating_count = f"{rating_count:,}"
        report += f"| {date} | {rating} | {rating_count} | {installs} |\n"

    # Rating Distribution (Android histogram if available)
    if android_entries:
        latest_android = android_entries[-1]
        histogram = latest_android.get("histogram")
        if histogram and len(histogram) == 5:
            report += """
---

## Google Play Rating Distribution (Current)

| Stars | Count | Percentage |
|-------|-------|------------|
"""
            total_ratings = sum(histogram)
            for i, count in enumerate(reversed(histogram), 1):
                star = 6 - i
                pct = (count / total_ratings * 100) if total_ratings > 0 else 0
                report += f"| {star} | {count:,} | {pct:.1f}% |\n"

    report += """
---

*Generated by Weekly Friday Scraper - Rating History Module*
"""

    # Save the report
    report_file = os.path.join(INSIGHTS_DIR, "Rating_History_Report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  Generated Rating History Report: {os.path.basename(report_file)}")

    # Also generate JSON report
    generate_rating_history_json()

    return report


# ============================================================================
# iOS SCRAPERS
# ============================================================================

def scrape_ios_reviews(country="us", max_reviews=3000):
    """Scrape iOS App Store reviews using app-store-scraper"""
    print(f"\n  Scraping iOS reviews for {country.upper()}...")

    try:
        from app_store_scraper import AppStore
    except ImportError:
        print("  ERROR: app-store-scraper not installed")
        return []

    try:
        app = AppStore(
            country=country,
            app_name=APP_CONFIG["ios"]["app_name"],
            app_id=APP_CONFIG["ios"]["app_id"]
        )

        app.review(how_many=max_reviews)

        reviews = []
        for review in app.reviews:
            review_date = review.get('date')
            reviews.append({
                "id": str(review.get('id', '')),
                "author": review.get('userName', 'Unknown'),
                "rating": review.get('rating', 0),
                "title": review.get('title', ''),
                "content": review.get('review', ''),
                "version": review.get('version', ''),
                "date": review_date.isoformat() if review_date else '',
                "country": country,
                "platform": "iOS App Store",
                "vote_count": review.get('voteCount', 0),
            })

        print(f"  Fetched {len(reviews)} iOS reviews from {country.upper()}")
        return reviews

    except Exception as e:
        print(f"  Error scraping iOS {country}: {e}")
        return []


def scrape_ios_all_countries(max_reviews_per_country=500):
    """Scrape iOS reviews from all configured countries"""
    all_reviews = []

    for country in ALL_COUNTRIES:
        reviews = scrape_ios_reviews(country, max_reviews=max_reviews_per_country)
        all_reviews.extend(reviews)

    return all_reviews


# ============================================================================
# ANDROID SCRAPERS
# ============================================================================

def scrape_android_reviews(country="us", max_reviews=500):
    """Scrape Google Play Store reviews"""
    print(f"\n  Scraping Android reviews for {country.upper()}...")

    try:
        from google_play_scraper import reviews, Sort
    except ImportError:
        print("  ERROR: google-play-scraper not installed")
        return []

    lang = COUNTRY_LANGUAGE_MAP.get(country, "en")
    all_reviews = []
    continuation_token = None
    batch_size = 100

    try:
        fetched = 0
        while fetched < max_reviews:
            result, continuation_token = reviews(
                APP_CONFIG["android"]["package_id"],
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=min(batch_size, max_reviews - fetched),
                continuation_token=continuation_token
            )

            if not result:
                break

            for review in result:
                review_date = review.get('at')
                all_reviews.append({
                    "id": review.get("reviewId", ""),
                    "author": review.get("userName", "Unknown"),
                    "rating": review.get("score", 0),
                    "title": "",
                    "content": review.get("content", ""),
                    "version": review.get("reviewCreatedVersion", ""),
                    "date": review_date.isoformat() if review_date else "",
                    "country": country,
                    "platform": "Google Play",
                    "vote_count": review.get("thumbsUpCount", 0),
                    "reply_content": review.get("replyContent", ""),
                })

            fetched += len(result)

            if continuation_token is None:
                break

        print(f"  Fetched {len(all_reviews)} Android reviews from {country.upper()}")
        return all_reviews

    except Exception as e:
        print(f"  Error scraping Android {country}: {e}")
        return all_reviews


def scrape_android_all_countries(max_reviews_per_country=500):
    """Scrape Android reviews from all configured countries"""
    all_reviews = []

    for country in ALL_COUNTRIES:
        reviews = scrape_android_reviews(country, max_reviews=max_reviews_per_country)
        all_reviews.extend(reviews)

    return all_reviews


# ============================================================================
# INSIGHTS AGENT
# ============================================================================

def run_insights_agent(reviews_file, output_name):
    """Run the CustomerInsight_Review_Agent on a data file"""
    print(f"\n  Running Insights Agent on {os.path.basename(reviews_file)}...")

    # Import the agent
    sys.path.insert(0, PROJECT_ROOT)
    try:
        from CustomerInsight_Review_Agent import load_reviews, analyze_reviews, save_insights_json
    except ImportError:
        print("  ERROR: CustomerInsight_Review_Agent not found")
        return None

    # Load and analyze
    reviews = load_reviews(reviews_file)
    if not reviews:
        print("  No reviews to analyze")
        return None

    analysis = analyze_reviews(reviews)

    # Save insights JSON
    json_output = os.path.join(REPORTS_DIR, f"{output_name}_Insights.json")
    save_insights_json(analysis, json_output)

    # Generate markdown report
    md_output = os.path.join(INSIGHTS_DIR, f"{output_name}_Insights.md")
    generate_insights_markdown(analysis, reviews_file, md_output, output_name)

    return analysis


def generate_insights_markdown(analysis, source_file, output_file, title):
    """Generate a markdown insights report"""
    total = analysis["total_reviews"]
    sent = analysis["sentiment_counts"]
    ratings = analysis["rating_distribution"]

    pos_pct = sent.get("positive", 0) / total * 100 if total > 0 else 0
    neg_pct = sent.get("negative", 0) / total * 100 if total > 0 else 0

    avg_rating = sum(r * c for r, c in ratings.items()) / total if total > 0 else 0

    # Determine platform from title for rating history
    platform = None
    if "iOS" in title:
        platform = "ios"
    elif "Android" in title:
        platform = "android"

    # Get current app store rating and trend
    current_ratings = {}
    rating_trend = None
    if os.path.exists(os.path.join(DATA_DIR, "current_app_ratings.json")):
        try:
            with open(os.path.join(DATA_DIR, "current_app_ratings.json"), 'r') as f:
                current_ratings = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    if platform:
        rating_trend = get_rating_trend(platform, days=30)

    # Build App Store Rating section
    app_store_rating_section = ""
    if platform and current_ratings:
        platform_ratings = current_ratings.get(platform, {}).get("us", {})
        if platform_ratings and platform_ratings.get("rating"):
            store_rating = platform_ratings.get("rating")
            rating_count = platform_ratings.get("rating_count", "N/A")
            store_name = "App Store" if platform == "ios" else "Play Store"

            app_store_rating_section = f"""
---

## {store_name} Rating

| Metric | Value |
|--------|-------|
| Current Store Rating | **{store_rating:.2f}** / 5.0 |
| Total Ratings | {rating_count:,} |
"""
            if platform == "ios" and platform_ratings.get("current_version_rating"):
                app_store_rating_section += f"| Current Version Rating | {platform_ratings.get('current_version_rating'):.2f} |\n"

            if platform == "android" and platform_ratings.get("installs"):
                app_store_rating_section += f"| Total Installs | {platform_ratings.get('installs')} |\n"

            # Add trend information
            if rating_trend and rating_trend.get("trend") != "insufficient_data":
                trend_emoji = ""
                if rating_trend["trend"] == "improving":
                    trend_emoji = "(trending up)"
                elif rating_trend["trend"] == "declining":
                    trend_emoji = "(trending down)"
                else:
                    trend_emoji = "(stable)"

                app_store_rating_section += f"""
### 30-Day Rating Trend

| Metric | Value |
|--------|-------|
| Trend | {rating_trend['trend'].title()} {trend_emoji} |
| Change | {rating_trend['change']:+.2f} |
| Average (30 days) | {rating_trend['avg_rating']:.2f} |
| Range | {rating_trend['min_rating']:.2f} - {rating_trend['max_rating']:.2f} |
| Data Points | {rating_trend['entries']} |
"""

    report = f"""# {title} - Customer Insights Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Source:** {os.path.basename(source_file)}
**Total Reviews:** {total}
{app_store_rating_section}
---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Reviews | {total} |
| Average Rating (from reviews) | {avg_rating:.2f} / 5.0 |
| Positive Sentiment | {pos_pct:.1f}% |
| Negative Sentiment | {neg_pct:.1f}% |
| 1-Star Reviews | {ratings.get(1, 0)} ({ratings.get(1, 0)/total*100:.1f}%) |
| 5-Star Reviews | {ratings.get(5, 0)} ({ratings.get(5, 0)/total*100:.1f}%) |

---

## Rating Distribution

| Stars | Count | Percentage |
|-------|-------|------------|
"""

    for star in range(5, 0, -1):
        count = ratings.get(star, 0)
        pct = count / total * 100 if total > 0 else 0
        report += f"| {star} | {count} | {pct:.1f}% |\n"

    report += """
---

## Top Issue Categories

| Rank | Category | Mentions | % of Reviews |
|------|----------|----------|--------------|
"""

    from CustomerInsight_Review_Agent import INSIGHT_CATEGORIES

    for rank, (cat_id, count) in enumerate(analysis["category_counts"].most_common(10), 1):
        if cat_id == "uncategorized":
            cat_name = "Other"
        else:
            cat_name = INSIGHT_CATEGORIES.get(cat_id, {}).get("name", cat_id)
        pct = count / total * 100 if total > 0 else 0
        report += f"| {rank} | {cat_name} | {count} | {pct:.1f}% |\n"

    report += f"""
---

## Critical Pain Points

"""

    # Find pain points
    for cat_id, count in analysis["category_counts"].most_common(10):
        if cat_id != "uncategorized":
            cat_sent = analysis["category_sentiment"].get(cat_id, {})
            neg_ratio = cat_sent.get("negative", 0) / count if count > 0 else 0
            if neg_ratio > 0.4:
                cat_name = INSIGHT_CATEGORIES.get(cat_id, {}).get("name", cat_id)
                report += f"- **{cat_name}**: {neg_ratio*100:.0f}% negative sentiment ({count} mentions)\n"

    report += """
---

*Generated by CustomerInsight_Review_Agent v1.1*
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"  Saved insights report to {os.path.basename(output_file)}")


# ============================================================================
# MAIN WEEKLY SCRAPER
# ============================================================================

def run_weekly_scrape():
    """
    Main weekly scraping function.

    Collects:
    1. iOS US - Last 30 days rolling
    2. iOS All Countries - Last 30 days rolling
    3. iOS US - Last 500 reviews
    4. Android US - Last 30 days rolling
    5. Android All Countries - Last 30 days rolling
    6. Android US - Last 500 reviews
    7. Combined iOS + Android US
    """
    print("\n" + "="*70)
    print("  WEEKLY FRIDAY SCRAPER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    results = {}

    # -------------------------------------------------------------------------
    # 0. Record Current App Store Ratings (Historical Tracking)
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("  [0/7] Recording App Store Ratings (iOS & Android)")
    print("-"*70)

    current_ratings = record_app_ratings()

    # -------------------------------------------------------------------------
    # 1. iOS US - Last 30 Days Rolling
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("  [1/7] iOS US - Last 30 Days Rolling")
    print("-"*70)

    ios_us_30d_file = os.path.join(IOS_DATA_DIR, "HP_App_iOS_US_Last30Days.json")
    existing_ios_us_30d = load_existing_reviews(ios_us_30d_file)

    new_ios_us = scrape_ios_reviews(country="us", max_reviews=3000)

    if new_ios_us:
        # Deduplicate
        merged = deduplicate_reviews(existing_ios_us_30d, new_ios_us)
        # Filter to last 30 days
        filtered = filter_reviews_by_date(merged, 30)
        # Save
        save_reviews(filtered, ios_us_30d_file)
        save_to_csv(filtered, ios_us_30d_file.replace('.json', '.csv'))
        # Analytics
        analytics = generate_analytics(filtered, "iOS App Store", "US", days=30)
        save_reviews(analytics, ios_us_30d_file.replace('.json', '_Analytics.json'))
        results['ios_us_30d'] = len(filtered)

    # -------------------------------------------------------------------------
    # 2. iOS All Countries - Last 30 Days Rolling
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("  [2/7] iOS All Countries - Last 30 Days Rolling")
    print("-"*70)

    ios_all_30d_file = os.path.join(IOS_DATA_DIR, "HP_App_iOS_AllCountries_Last30Days.json")
    existing_ios_all_30d = load_existing_reviews(ios_all_30d_file)

    new_ios_all = scrape_ios_all_countries(max_reviews_per_country=500)

    if new_ios_all:
        merged = deduplicate_reviews(existing_ios_all_30d, new_ios_all)
        filtered = filter_reviews_by_date(merged, 30)
        save_reviews(filtered, ios_all_30d_file)
        save_to_csv(filtered, ios_all_30d_file.replace('.json', '.csv'))
        analytics = generate_analytics(filtered, "iOS App Store", "AllCountries", days=30)
        save_reviews(analytics, ios_all_30d_file.replace('.json', '_Analytics.json'))
        results['ios_all_30d'] = len(filtered)

    # -------------------------------------------------------------------------
    # 3. iOS US - Last 500 Reviews
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("  [3/7] iOS US - Last 500 Reviews")
    print("-"*70)

    ios_us_500_file = os.path.join(IOS_DATA_DIR, "HP_App_iOS_US_Last500.json")
    existing_ios_500 = load_existing_reviews(ios_us_500_file)

    # Use reviews already fetched in step 1
    if new_ios_us:
        merged = deduplicate_reviews(existing_ios_500, new_ios_us)
        # Keep only latest 500
        latest_500 = merged[:500]
        save_reviews(latest_500, ios_us_500_file)
        save_to_csv(latest_500, ios_us_500_file.replace('.json', '.csv'))
        analytics = generate_analytics(latest_500, "iOS App Store", "US")
        save_reviews(analytics, ios_us_500_file.replace('.json', '_Analytics.json'))
        results['ios_us_500'] = len(latest_500)

    # -------------------------------------------------------------------------
    # 4. Android US - Last 30 Days Rolling
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("  [4/7] Android US - Last 30 Days Rolling")
    print("-"*70)

    android_us_30d_file = os.path.join(ANDROID_DATA_DIR, "HP_App_Android_US_Last30Days.json")
    existing_android_us_30d = load_existing_reviews(android_us_30d_file)

    new_android_us = scrape_android_reviews(country="us", max_reviews=3000)

    if new_android_us:
        merged = deduplicate_reviews(existing_android_us_30d, new_android_us)
        filtered = filter_reviews_by_date(merged, 30)
        save_reviews(filtered, android_us_30d_file)
        save_to_csv(filtered, android_us_30d_file.replace('.json', '.csv'))
        analytics = generate_analytics(filtered, "Google Play", "US", days=30)
        save_reviews(analytics, android_us_30d_file.replace('.json', '_Analytics.json'))
        results['android_us_30d'] = len(filtered)

    # -------------------------------------------------------------------------
    # 5. Android All Countries - Last 30 Days Rolling
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("  [5/7] Android All Countries - Last 30 Days Rolling")
    print("-"*70)

    android_all_30d_file = os.path.join(ANDROID_DATA_DIR, "HP_App_Android_AllCountries_Last30Days.json")
    existing_android_all_30d = load_existing_reviews(android_all_30d_file)

    new_android_all = scrape_android_all_countries(max_reviews_per_country=500)

    if new_android_all:
        merged = deduplicate_reviews(existing_android_all_30d, new_android_all)
        filtered = filter_reviews_by_date(merged, 30)
        save_reviews(filtered, android_all_30d_file)
        save_to_csv(filtered, android_all_30d_file.replace('.json', '.csv'))
        analytics = generate_analytics(filtered, "Google Play", "AllCountries", days=30)
        save_reviews(analytics, android_all_30d_file.replace('.json', '_Analytics.json'))
        results['android_all_30d'] = len(filtered)

    # -------------------------------------------------------------------------
    # 6. Android US - Last 500 Reviews
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("  [6/7] Android US - Last 500 Reviews")
    print("-"*70)

    android_us_500_file = os.path.join(ANDROID_DATA_DIR, "HP_App_Android_US_Last500.json")
    existing_android_500 = load_existing_reviews(android_us_500_file)

    # Use reviews already fetched in step 4
    if new_android_us:
        merged = deduplicate_reviews(existing_android_500, new_android_us)
        latest_500 = merged[:500]
        save_reviews(latest_500, android_us_500_file)
        save_to_csv(latest_500, android_us_500_file.replace('.json', '.csv'))
        analytics = generate_analytics(latest_500, "Google Play", "US")
        save_reviews(analytics, android_us_500_file.replace('.json', '_Analytics.json'))
        results['android_us_500'] = len(latest_500)

    # -------------------------------------------------------------------------
    # 7. Run Insights Agent on All Data
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("  [7/7] Running CustomerInsight_Review_Agent")
    print("-"*70)

    # Run insights on each dataset
    # iOS datasets
    if os.path.exists(ios_us_30d_file):
        run_insights_agent(ios_us_30d_file, "HP_App_iOS_US_Last30Days")

    if os.path.exists(ios_all_30d_file):
        run_insights_agent(ios_all_30d_file, "HP_App_iOS_AllCountries_Last30Days")

    if os.path.exists(ios_us_500_file):
        run_insights_agent(ios_us_500_file, "HP_App_iOS_US_Last500")

    # Android datasets
    if os.path.exists(android_us_30d_file):
        run_insights_agent(android_us_30d_file, "HP_App_Android_US_Last30Days")

    if os.path.exists(android_all_30d_file):
        run_insights_agent(android_all_30d_file, "HP_App_Android_AllCountries_Last30Days")

    if os.path.exists(android_us_500_file):
        run_insights_agent(android_us_500_file, "HP_App_Android_US_Last500")

    # Combined iOS + Android US analysis (using 30-day rolling data)
    combined_file = os.path.join(DATA_DIR, "HP_App_Combined_US_Last30Days.json")
    combined_reviews = []

    if os.path.exists(ios_us_30d_file):
        combined_reviews.extend(load_existing_reviews(ios_us_30d_file))
    if os.path.exists(android_us_30d_file):
        combined_reviews.extend(load_existing_reviews(android_us_30d_file))

    if combined_reviews:
        save_reviews(combined_reviews, combined_file)
        run_insights_agent(combined_file, "HP_App_Combined_US_Last30Days")
        results['combined_us_30d'] = len(combined_reviews)

    # Combined All Countries analysis
    combined_all_file = os.path.join(DATA_DIR, "HP_App_Combined_AllCountries_Last30Days.json")
    combined_all_reviews = []

    if os.path.exists(ios_all_30d_file):
        combined_all_reviews.extend(load_existing_reviews(ios_all_30d_file))
    if os.path.exists(android_all_30d_file):
        combined_all_reviews.extend(load_existing_reviews(android_all_30d_file))

    if combined_all_reviews:
        save_reviews(combined_all_reviews, combined_all_file)
        run_insights_agent(combined_all_file, "HP_App_Combined_AllCountries_Last30Days")
        results['combined_all_30d'] = len(combined_all_reviews)

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("  WEEKLY SCRAPE COMPLETE")
    print("="*70)

    print("\n  Results Summary:")
    for key, count in results.items():
        print(f"    {key}: {count} reviews")

    # Print current ratings
    if current_ratings:
        print("\n  App Store Ratings:")
        ios_rating = current_ratings.get("ios", {}).get("us", {})
        android_rating = current_ratings.get("android", {}).get("us", {})
        if ios_rating and ios_rating.get("rating"):
            print(f"    iOS (US): {ios_rating['rating']:.2f} / 5.0")
        if android_rating and android_rating.get("rating"):
            print(f"    Android (US): {android_rating['rating']:.2f} / 5.0")

    # Generate Rating History Report
    generate_rating_history_report()

    # Save summary for GitHub Actions
    summary = {
        "scrape_date": datetime.now().isoformat(),
        "results": results,
        "total_reviews": sum(results.values()),
        "app_ratings": {
            "ios_us": current_ratings.get("ios", {}).get("us", {}).get("rating") if current_ratings else None,
            "android_us": current_ratings.get("android", {}).get("us", {}).get("rating") if current_ratings else None,
        },
        "rating_trends": {
            "ios": get_rating_trend("ios", days=30),
            "android": get_rating_trend("android", days=30),
        }
    }
    summary_file = os.path.join(REPORTS_DIR, "weekly_summary.json")
    save_reviews(summary, summary_file)

    print(f"\n  Total reviews collected: {sum(results.values())}")
    print(f"  Summary saved to: {summary_file}")

    return results


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Weekly Friday Scraper")
    parser.add_argument("--all", action="store_true", help="Run full weekly scrape")
    parser.add_argument("--ios-only", action="store_true", help="Scrape iOS only")
    parser.add_argument("--android-only", action="store_true", help="Scrape Android only")
    parser.add_argument("--insights-only", action="store_true", help="Run insights only (no scraping)")
    parser.add_argument("--ratings-only", action="store_true", help="Record app store ratings only")
    parser.add_argument("--rating-report", action="store_true", help="Generate rating history report only")

    args = parser.parse_args()

    if args.ratings_only:
        # Just record current app ratings
        print("Recording app store ratings...")
        current_ratings = record_app_ratings()
        if current_ratings:
            ios_r = current_ratings.get("ios", {}).get("us", {})
            android_r = current_ratings.get("android", {}).get("us", {})
            if ios_r and ios_r.get("rating"):
                print(f"  iOS (US): {ios_r['rating']:.2f}")
            if android_r and android_r.get("rating"):
                print(f"  Android (US): {android_r['rating']:.2f}")
        generate_rating_history_report()
        print("Done!")
    elif args.rating_report:
        # Just generate the rating history report
        print("Generating rating history report...")
        generate_rating_history_report()
        print("Done!")
    elif args.insights_only:
        # Just run insights on existing data
        print("Running insights only...")
        data_files = [
            # iOS datasets
            os.path.join(IOS_DATA_DIR, "HP_App_iOS_US_Last30Days.json"),
            os.path.join(IOS_DATA_DIR, "HP_App_iOS_AllCountries_Last30Days.json"),
            os.path.join(IOS_DATA_DIR, "HP_App_iOS_US_Last500.json"),
            # Android datasets
            os.path.join(ANDROID_DATA_DIR, "HP_App_Android_US_Last30Days.json"),
            os.path.join(ANDROID_DATA_DIR, "HP_App_Android_AllCountries_Last30Days.json"),
            os.path.join(ANDROID_DATA_DIR, "HP_App_Android_US_Last500.json"),
            # Combined datasets
            os.path.join(DATA_DIR, "HP_App_Combined_US_Last30Days.json"),
            os.path.join(DATA_DIR, "HP_App_Combined_AllCountries_Last30Days.json"),
        ]
        for data_file in data_files:
            if os.path.exists(data_file):
                name = os.path.basename(data_file).replace('.json', '')
                run_insights_agent(data_file, name)
        # Also generate rating history report
        generate_rating_history_report()
    else:
        # Run full weekly scrape
        run_weekly_scrape()
