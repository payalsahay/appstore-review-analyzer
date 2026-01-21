"""
Google Play HP App - October 2025 onwards Analysis
Product Manager perspective: Top 5 user issues
"""

import json
import csv
import re
from datetime import datetime
from collections import Counter

# Load reviews
with open("GooglePlay_HP_app.json", "r") as f:
    all_reviews = json.load(f)

print(f"Total reviews loaded: {len(all_reviews)}")

# Filter for October 2025 onwards
oct_reviews = []
for review in all_reviews:
    date_str = review.get("date", "")
    if date_str:
        try:
            review_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            # October 2025 onwards
            if review_date >= datetime(2025, 10, 1):
                oct_reviews.append(review)
        except:
            pass

print(f"Reviews from Oct 2025 onwards: {len(oct_reviews)}")

# ============================================================================
# ISSUE CATEGORIZATION
# ============================================================================

# Define issue categories with keywords
ISSUE_CATEGORIES = {
    "connectivity_offline": {
        "name": "Printer Connectivity / Goes Offline",
        "keywords": ["offline", "connect", "connection", "wifi", "network", "disconnect",
                     "not connecting", "won't connect", "can't connect", "cannot connect",
                     "finds", "find printer", "detect", "discovered", "bluetooth", "wireless",
                     "reconnect", "lost connection", "no connection", "keeps disconnecting"],
        "count": 0,
        "reviews": []
    },
    "printing_issues": {
        "name": "Printing Problems / Print Jobs Fail",
        "keywords": ["print", "printing", "won't print", "not printing", "can't print",
                     "print job", "queue", "stuck", "blank page", "doesn't print",
                     "failed to print", "print fails", "won't let me print", "printing error"],
        "count": 0,
        "reviews": []
    },
    "scanning_issues": {
        "name": "Scanning / Copy Functionality Issues",
        "keywords": ["scan", "scanning", "scanner", "copy", "copies", "won't scan",
                     "can't scan", "scan feature", "scan function", "scanning not working",
                     "document scan", "photo scan"],
        "count": 0,
        "reviews": []
    },
    "app_crashes_bugs": {
        "name": "App Crashes / Bugs / Freezes",
        "keywords": ["crash", "crashes", "bug", "bugs", "freeze", "freezes", "frozen",
                     "glitch", "error", "not working", "doesn't work", "broken",
                     "force close", "keeps closing", "stops working", "unresponsive",
                     "laggy", "slow", "hangs"],
        "count": 0,
        "reviews": []
    },
    "login_account": {
        "name": "Login / Account / Sign-in Problems",
        "keywords": ["login", "log in", "sign in", "signin", "account", "password",
                     "email", "verification", "verify", "authenticate", "authentication",
                     "can't login", "won't sign", "sign up", "registration", "hp account",
                     "create account", "forgot password"],
        "count": 0,
        "reviews": []
    },
    "setup_installation": {
        "name": "Setup / Installation Difficulties",
        "keywords": ["setup", "set up", "install", "installation", "configure",
                     "add printer", "adding printer", "pairing", "initialize",
                     "first time", "new printer", "setting up"],
        "count": 0,
        "reviews": []
    },
    "update_issues": {
        "name": "Update Problems / Version Issues",
        "keywords": ["update", "updated", "upgrade", "new version", "after update",
                     "since update", "latest version", "downgrade", "previous version",
                     "worked before", "used to work", "old version", "recent update"],
        "count": 0,
        "reviews": []
    },
    "subscription_ads": {
        "name": "Subscription / Ads / HP+ Issues",
        "keywords": ["subscription", "subscribe", "hp+", "hp plus", "instant ink",
                     "payment", "pay", "money", "ads", "advertisement", "premium",
                     "free trial", "charge", "billing", "expensive", "cost"],
        "count": 0,
        "reviews": []
    },
    "ink_cartridge": {
        "name": "Ink / Cartridge Issues",
        "keywords": ["ink", "cartridge", "toner", "ink level", "ink status",
                     "low ink", "out of ink", "replace cartridge", "ink warning"],
        "count": 0,
        "reviews": []
    },
    "ui_ux_issues": {
        "name": "UI/UX / Hard to Use",
        "keywords": ["confusing", "complicated", "difficult", "hard to use",
                     "user friendly", "intuitive", "interface", "navigation",
                     "find", "where is", "can't find", "hidden", "cluttered"],
        "count": 0,
        "reviews": []
    }
}

def categorize_review(review):
    """Categorize a review into issue categories"""
    content = (review.get("content", "") or "").lower()
    categories_found = []

    for cat_id, cat_info in ISSUE_CATEGORIES.items():
        for keyword in cat_info["keywords"]:
            if keyword in content:
                categories_found.append(cat_id)
                break

    return categories_found

# Categorize all October reviews
for review in oct_reviews:
    categories = categorize_review(review)
    for cat_id in categories:
        ISSUE_CATEGORIES[cat_id]["count"] += 1
        # Store sample reviews (max 20 per category)
        if len(ISSUE_CATEGORIES[cat_id]["reviews"]) < 20:
            ISSUE_CATEGORIES[cat_id]["reviews"].append({
                "rating": review.get("rating"),
                "content": review.get("content"),
                "date": review.get("date"),
                "country": review.get("country"),
                "version": review.get("version")
            })

# Sort categories by count
sorted_categories = sorted(
    ISSUE_CATEGORIES.items(),
    key=lambda x: x[1]["count"],
    reverse=True
)

# ============================================================================
# ANALYTICS
# ============================================================================

# Rating distribution
ratings = [r.get("rating", 0) for r in oct_reviews]
rating_dist = Counter(ratings)
avg_rating = sum(ratings) / len(ratings) if ratings else 0

# Country distribution
country_dist = Counter(r.get("country", "unknown") for r in oct_reviews)

# Version distribution
version_dist = Counter(r.get("version", "unknown") for r in oct_reviews)

# Weekly trend (simplified)
from collections import defaultdict
weekly_ratings = defaultdict(list)
for review in oct_reviews:
    date_str = review.get("date", "")
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            week_key = dt.strftime("%Y-W%W")
            weekly_ratings[week_key].append(review.get("rating", 0))
        except:
            pass

weekly_avg = {k: sum(v)/len(v) for k, v in sorted(weekly_ratings.items())}

# ============================================================================
# OUTPUT
# ============================================================================

print("\n" + "="*70)
print("HP SMART APP - GOOGLE PLAY STORE ANALYSIS")
print("Period: October 2025 onwards")
print("="*70)

print(f"\n📊 OVERVIEW")
print(f"   Total Reviews: {len(oct_reviews)}")
print(f"   Average Rating: {avg_rating:.2f} / 5.0")
print(f"   1-Star Reviews: {rating_dist.get(1, 0)} ({rating_dist.get(1, 0)/len(oct_reviews)*100:.1f}%)")
print(f"   5-Star Reviews: {rating_dist.get(5, 0)} ({rating_dist.get(5, 0)/len(oct_reviews)*100:.1f}%)")

print(f"\n📉 RATING DISTRIBUTION")
for star in range(5, 0, -1):
    count = rating_dist.get(star, 0)
    pct = count / len(oct_reviews) * 100 if oct_reviews else 0
    bar = "█" * int(pct / 2)
    print(f"   {star}★: {count:4d} ({pct:5.1f}%) {bar}")

print(f"\n🔥 TOP 5 USER ISSUES (Product Manager Analysis)")
print("-"*70)

top_5_issues = []
for i, (cat_id, cat_info) in enumerate(sorted_categories[:5], 1):
    pct = cat_info["count"] / len(oct_reviews) * 100 if oct_reviews else 0
    print(f"\n{i}. {cat_info['name'].upper()}")
    print(f"   Mentions: {cat_info['count']} reviews ({pct:.1f}% of all reviews)")

    # Get sample negative reviews for this category
    negative_samples = [r for r in cat_info["reviews"] if r["rating"] <= 2][:3]

    print(f"   Sample complaints:")
    for sample in negative_samples:
        content = sample["content"][:120] + "..." if len(sample.get("content", "") or "") > 120 else sample.get("content", "")
        print(f"   • \"{content}\" [{sample['rating']}★, {sample['country'].upper()}]")

    top_5_issues.append({
        "rank": i,
        "issue": cat_info["name"],
        "mention_count": cat_info["count"],
        "percentage": round(pct, 1),
        "sample_reviews": cat_info["reviews"][:5]
    })

# ============================================================================
# SAVE FILES
# ============================================================================

# Save filtered reviews
with open("GooglePlay_HP_Oct_Reviews.json", "w", encoding="utf-8") as f:
    json.dump(oct_reviews, f, indent=2, ensure_ascii=False, default=str)
print(f"\n✅ Saved: GooglePlay_HP_Oct_Reviews.json ({len(oct_reviews)} reviews)")

# Save CSV
fieldnames = ["id", "author", "rating", "content", "version", "date", "country", "language", "vote_count"]
with open("GooglePlay_HP_Oct_Reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(oct_reviews)
print(f"✅ Saved: GooglePlay_HP_Oct_Reviews.csv")

# Save analytics
analytics = {
    "period": "October 2025 onwards",
    "total_reviews": len(oct_reviews),
    "average_rating": round(avg_rating, 2),
    "rating_distribution": dict(sorted(rating_dist.items(), reverse=True)),
    "country_distribution": dict(country_dist.most_common()),
    "version_distribution": dict(version_dist.most_common(10)),
    "weekly_average_rating": weekly_avg,
    "analysis_date": datetime.now().isoformat()
}

with open("GooglePlay_HP_Oct_Analytics.json", "w", encoding="utf-8") as f:
    json.dump(analytics, f, indent=2, ensure_ascii=False, default=str)
print(f"✅ Saved: GooglePlay_HP_Oct_Analytics.json")

# Save Top 5 Issues Analysis
pm_analysis = {
    "title": "HP Smart App - Google Play Store - Top User Issues",
    "period": "October 2025 onwards",
    "total_reviews_analyzed": len(oct_reviews),
    "average_rating": round(avg_rating, 2),
    "top_5_issues": top_5_issues,
    "all_issue_categories": {
        cat_id: {
            "name": cat_info["name"],
            "count": cat_info["count"],
            "percentage": round(cat_info["count"] / len(oct_reviews) * 100, 1) if oct_reviews else 0
        }
        for cat_id, cat_info in sorted_categories
    },
    "analysis_date": datetime.now().isoformat()
}

with open("GooglePlay_HP_Oct_TopIssues.json", "w", encoding="utf-8") as f:
    json.dump(pm_analysis, f, indent=2, ensure_ascii=False, default=str)
print(f"✅ Saved: GooglePlay_HP_Oct_TopIssues.json")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
