#!/usr/bin/env python3
"""
================================================================================
AUTOMATED APP STORE REVIEW ANALYSIS PIPELINE
================================================================================

This script orchestrates the entire analysis pipeline:
1. SCRAPE  - Collect reviews from iOS App Store & Google Play
2. ANALYZE - Run CustomerInsight_Review_Agent analysis
3. VISUALIZE - Generate executive dashboards
4. REPORT - Create PM insights reports

Usage:
    python automated_pipeline.py --scrape      # Collect latest reviews
    python automated_pipeline.py --analyze     # Run analysis
    python automated_pipeline.py --visualize   # Generate charts
    python automated_pipeline.py --report      # Generate report
    python automated_pipeline.py --all         # Run full pipeline

Author: CustomerInsight_Review_Agent
Version: 2.0
================================================================================
"""

import argparse
import json
import os
import sys
from datetime import datetime
from collections import Counter, defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "app_name": "HP App",
    "ios_app_id": 469284907,
    "android_package": "com.hp.printercontrol",
    "target_country": "us",
    "data_dir": "data",
    "output_dir": "output",
    "reports_dir": "output/reports",
    "viz_dir": "output/visualizations",
}

# ============================================================================
# CUSTOMERINSIGHT_REVIEW_AGENT CATEGORIES
# ============================================================================

INSIGHT_CATEGORIES = {
    "connectivity": {
        "name": "Connectivity & Setup",
        "keywords": ["wifi", "wi-fi", "connect", "connection", "network", "bluetooth",
                     "setup", "find printer", "discover", "pair", "wireless", "offline"],
    },
    "printing": {
        "name": "Print Quality & Functionality",
        "keywords": ["print", "printing", "quality", "resolution", "color", "pages",
                     "paper", "ink", "toner", "cartridge", "jam", "duplex", "photo"],
    },
    "scanning": {
        "name": "Scanning Features",
        "keywords": ["scan", "scanning", "scanner", "ocr", "document", "image"],
    },
    "mobile_experience": {
        "name": "Mobile App Experience",
        "keywords": ["app", "interface", "easy", "difficult", "confusing", "intuitive",
                     "simple", "complicated", "navigate", "menu", "button"],
    },
    "reliability": {
        "name": "App Reliability & Stability",
        "keywords": ["crash", "bug", "freeze", "frozen", "stuck", "error", "fail",
                     "not working", "broken", "glitch", "slow", "lag"],
    },
    "updates": {
        "name": "Updates & Compatibility",
        "keywords": ["update", "version", "ios", "android", "compatible", "upgrade"],
    },
    "features": {
        "name": "Feature Requests",
        "keywords": ["wish", "want", "need", "should", "missing", "add", "feature"],
    },
    "account_cloud": {
        "name": "Account & Cloud Services",
        "keywords": ["login", "sign in", "account", "password", "cloud", "email"],
    },
    "support": {
        "name": "Customer Support",
        "keywords": ["support", "help", "customer service", "contact", "troubleshoot"],
    },
    "value": {
        "name": "Value & Pricing",
        "keywords": ["subscription", "hp+", "instant ink", "payment", "ads", "free", "paid"],
    },
}

SENTIMENT_KEYWORDS = {
    "positive": ["love", "great", "excellent", "amazing", "awesome", "perfect", "best",
                 "fantastic", "easy", "works great", "recommend", "good", "helpful"],
    "negative": ["hate", "terrible", "awful", "worst", "horrible", "bad", "poor",
                 "useless", "frustrating", "disappointing", "broken", "fail", "crash"],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def ensure_dirs():
    """Create necessary directories"""
    for dir_key in ["data_dir", "output_dir", "reports_dir", "viz_dir"]:
        os.makedirs(CONFIG[dir_key], exist_ok=True)
    os.makedirs(f"{CONFIG['data_dir']}/ios", exist_ok=True)
    os.makedirs(f"{CONFIG['data_dir']}/googleplay", exist_ok=True)


def analyze_sentiment(text):
    """Analyze sentiment of review text"""
    text_lower = text.lower()
    pos = sum(1 for w in SENTIMENT_KEYWORDS["positive"] if w in text_lower)
    neg = sum(1 for w in SENTIMENT_KEYWORDS["negative"] if w in text_lower)
    return "positive" if pos > neg else ("negative" if neg > pos else "neutral")


def categorize_review(text):
    """Categorize review into insight categories"""
    text_lower = text.lower()
    categories = []
    for cat_id, cat_info in INSIGHT_CATEGORIES.items():
        if any(kw in text_lower for kw in cat_info["keywords"]):
            categories.append(cat_id)
    return categories if categories else ["uncategorized"]


# ============================================================================
# 1. SCRAPE - Collect Reviews
# ============================================================================

def scrape_reviews():
    """Collect reviews from iOS App Store and Google Play"""
    print("\n" + "="*60)
    print("📥 SCRAPING REVIEWS")
    print("="*60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    all_reviews = {"ios": [], "googleplay": []}

    # iOS App Store
    try:
        from app_store_scraper import AppStore
        print(f"\n🍎 Scraping iOS App Store...")

        app = AppStore(country=CONFIG["target_country"],
                       app_name="hp-smart",
                       app_id=CONFIG["ios_app_id"])
        app.review(how_many=1000)

        for r in app.reviews:
            all_reviews["ios"].append({
                "id": r.get("id", ""),
                "author": r.get("userName", ""),
                "rating": r.get("rating", 0),
                "title": r.get("title", ""),
                "content": r.get("review", ""),
                "date": r.get("date").isoformat() if r.get("date") else "",
                "version": r.get("version", ""),
                "platform": "iOS"
            })

        print(f"   ✅ Collected {len(all_reviews['ios'])} iOS reviews")
    except Exception as e:
        print(f"   ❌ iOS scraping failed: {e}")

    # Google Play
    try:
        from google_play_scraper import reviews, Sort
        print(f"\n🤖 Scraping Google Play Store...")

        all_gplay = []
        token = None
        for _ in range(10):  # 10 batches x 200 = up to 2000 reviews
            result, token = reviews(
                CONFIG["android_package"],
                lang="en",
                country=CONFIG["target_country"],
                sort=Sort.NEWEST,
                count=200,
                continuation_token=token
            )
            all_gplay.extend(result)
            if not token:
                break

        for r in all_gplay:
            all_reviews["googleplay"].append({
                "id": r.get("reviewId", ""),
                "author": r.get("userName", ""),
                "rating": r.get("score", 0),
                "title": "",
                "content": r.get("content", ""),
                "date": r.get("at").isoformat() if r.get("at") else "",
                "version": r.get("reviewCreatedVersion", ""),
                "platform": "Android"
            })

        print(f"   ✅ Collected {len(all_reviews['googleplay'])} Android reviews")
    except Exception as e:
        print(f"   ❌ Google Play scraping failed: {e}")

    # Save data
    for platform, reviews_list in all_reviews.items():
        if reviews_list:
            filepath = f"{CONFIG['data_dir']}/{platform}/reviews_{timestamp}.json"
            with open(filepath, "w") as f:
                json.dump(reviews_list, f, indent=2, default=str)
            print(f"\n💾 Saved: {filepath}")

    return all_reviews


# ============================================================================
# 2. ANALYZE - Run CustomerInsight_Review_Agent
# ============================================================================

def analyze_reviews_data(reviews):
    """Run CustomerInsight_Review_Agent analysis"""
    print("\n" + "="*60)
    print("🧠 RUNNING ANALYSIS")
    print("="*60)

    results = {
        "total": len(reviews),
        "sentiment": Counter(),
        "ratings": Counter(),
        "categories": Counter(),
        "category_sentiment": defaultdict(lambda: Counter()),
        "category_samples": defaultdict(list),
    }

    for r in reviews:
        content = f"{r.get('title', '')} {r.get('content', '')}"
        rating = int(r.get("rating", 0))

        # Rating
        results["ratings"][rating] += 1

        # Sentiment
        sentiment = analyze_sentiment(content)
        results["sentiment"][sentiment] += 1

        # Categories
        cats = categorize_review(content)
        for cat in cats:
            results["categories"][cat] += 1
            results["category_sentiment"][cat][sentiment] += 1
            if len(results["category_samples"][cat]) < 5:
                results["category_samples"][cat].append({
                    "rating": rating,
                    "snippet": content[:200],
                    "sentiment": sentiment,
                    "platform": r.get("platform", "Unknown")
                })

    # Calculate averages
    total = results["total"]
    if total > 0:
        results["avg_rating"] = sum(r * c for r, c in results["ratings"].items()) / total
        results["positive_pct"] = results["sentiment"]["positive"] / total * 100
        results["negative_pct"] = results["sentiment"]["negative"] / total * 100
        results["one_star_pct"] = results["ratings"].get(1, 0) / total * 100

    print(f"\n📊 Analysis Summary:")
    print(f"   Total Reviews: {total}")
    print(f"   Average Rating: {results.get('avg_rating', 0):.2f}")
    print(f"   Negative Sentiment: {results.get('negative_pct', 0):.1f}%")

    return results


def run_analysis():
    """Load data and run analysis"""
    # Find latest data files
    all_reviews = []

    for platform in ["ios", "googleplay"]:
        data_path = f"{CONFIG['data_dir']}/{platform}"
        if os.path.exists(data_path):
            files = sorted([f for f in os.listdir(data_path) if f.endswith('.json')])
            if files:
                latest = files[-1]
                with open(f"{data_path}/{latest}") as f:
                    reviews = json.load(f)
                    all_reviews.extend(reviews)
                    print(f"📂 Loaded {len(reviews)} reviews from {platform}/{latest}")

    if not all_reviews:
        # Fallback to existing data files
        for filename in ["HP_App_GooglePlay_US_Oct2025_Full.json", "HP_App_iOS_US_Oct2025_Full.json"]:
            if os.path.exists(filename):
                with open(filename) as f:
                    reviews = json.load(f)
                    all_reviews.extend(reviews)
                    print(f"📂 Loaded {len(reviews)} reviews from {filename}")

    if all_reviews:
        results = analyze_reviews_data(all_reviews)

        # Save results
        output_path = f"{CONFIG['reports_dir']}/analysis_results.json"
        with open(output_path, "w") as f:
            json.dump({
                "analysis_date": datetime.now().isoformat(),
                "total_reviews": results["total"],
                "avg_rating": round(results.get("avg_rating", 0), 2),
                "sentiment": dict(results["sentiment"]),
                "ratings": dict(results["ratings"]),
                "top_issues": results["categories"].most_common(10),
            }, f, indent=2)
        print(f"\n💾 Saved: {output_path}")

        # Save summary for GitHub Actions
        summary_path = f"{CONFIG['reports_dir']}/summary.json"
        with open(summary_path, "w") as f:
            json.dump({
                "total_reviews": results["total"],
                "avg_rating": round(results.get("avg_rating", 0), 2),
                "negative_pct": round(results.get("negative_pct", 0), 1),
            }, f, indent=2)

        return results
    else:
        print("❌ No review data found!")
        return None


# ============================================================================
# 3. VISUALIZE - Generate Charts
# ============================================================================

def generate_visualizations():
    """Generate executive dashboards"""
    print("\n" + "="*60)
    print("📊 GENERATING VISUALIZATIONS")
    print("="*60)

    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches

        # Load analysis results
        results_path = f"{CONFIG['reports_dir']}/analysis_results.json"
        if not os.path.exists(results_path):
            print("❌ No analysis results found. Run --analyze first.")
            return

        with open(results_path) as f:
            data = json.load(f)

        # Create dashboard
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'{CONFIG["app_name"]} - Review Analysis Dashboard\n{datetime.now().strftime("%B %Y")}',
                     fontsize=14, fontweight='bold')

        # 1. Rating Distribution
        ax1 = axes[0, 0]
        ratings = data.get("ratings", {})
        stars = ['5★', '4★', '3★', '2★', '1★']
        counts = [ratings.get(str(5-i), 0) for i in range(5)]
        colors = ['#27ae60', '#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
        ax1.barh(stars, counts, color=colors)
        ax1.set_title('Rating Distribution')
        ax1.set_xlabel('Count')

        # 2. Sentiment
        ax2 = axes[0, 1]
        sentiment = data.get("sentiment", {})
        labels = ['Positive', 'Negative', 'Neutral']
        sizes = [sentiment.get(s.lower(), 0) for s in labels]
        colors = ['#27ae60', '#e74c3c', '#95a5a6']
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        ax2.set_title('Sentiment Distribution')

        # 3. Top Issues
        ax3 = axes[1, 0]
        top_issues = data.get("top_issues", [])[:5]
        if top_issues:
            issue_names = [INSIGHT_CATEGORIES.get(i[0], {}).get("name", i[0])[:15] for i in top_issues]
            issue_counts = [i[1] for i in top_issues]
            ax3.barh(issue_names[::-1], issue_counts[::-1], color='#3498db')
        ax3.set_title('Top 5 Issues')
        ax3.set_xlabel('Mentions')

        # 4. Key Metrics
        ax4 = axes[1, 1]
        ax4.axis('off')
        metrics_text = f"""
        KEY METRICS
        ═══════════════════════
        Total Reviews: {data.get('total_reviews', 0):,}
        Average Rating: {data.get('avg_rating', 0):.2f} / 5.0
        Negative Sentiment: {data.get('sentiment', {}).get('negative', 0) / max(data.get('total_reviews', 1), 1) * 100:.1f}%
        1-Star Reviews: {data.get('ratings', {}).get('1', 0):,}

        Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
        """
        ax4.text(0.1, 0.5, metrics_text, fontsize=12, fontfamily='monospace',
                 verticalalignment='center')

        plt.tight_layout()

        # Save
        viz_path = f"{CONFIG['viz_dir']}/executive_dashboard.png"
        plt.savefig(viz_path, dpi=150, bbox_inches='tight')
        print(f"💾 Saved: {viz_path}")
        plt.close()

    except ImportError:
        print("❌ matplotlib not installed. Skipping visualizations.")


# ============================================================================
# 4. REPORT - Generate PM Insights
# ============================================================================

def generate_report():
    """Generate PM insights report"""
    print("\n" + "="*60)
    print("📝 GENERATING REPORT")
    print("="*60)

    results_path = f"{CONFIG['reports_dir']}/analysis_results.json"
    if not os.path.exists(results_path):
        print("❌ No analysis results found. Run --analyze first.")
        return

    with open(results_path) as f:
        data = json.load(f)

    # Generate Markdown report
    report = f"""# {CONFIG['app_name']} - Customer Insights Report
## {datetime.now().strftime('%B %Y')}

---

**Generated by:** CustomerInsight_Review_Agent v2.0
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Reviews Analyzed | {data.get('total_reviews', 0):,} |
| Average Rating | {data.get('avg_rating', 0):.2f} / 5.0 |
| Negative Sentiment | {data.get('sentiment', {}).get('negative', 0) / max(data.get('total_reviews', 1), 1) * 100:.1f}% |
| 1-Star Reviews | {data.get('ratings', {}).get('1', 0):,} |

---

## Rating Distribution

| Rating | Count | Percentage |
|--------|-------|------------|
"""

    total = data.get('total_reviews', 1)
    for r in range(5, 0, -1):
        count = data.get('ratings', {}).get(str(r), 0)
        pct = count / total * 100
        report += f"| {'⭐' * r} | {count:,} | {pct:.1f}% |\n"

    report += f"""
---

## Top Customer Issues

| Rank | Issue | Mentions |
|------|-------|----------|
"""

    for rank, (cat_id, count) in enumerate(data.get('top_issues', [])[:10], 1):
        cat_name = INSIGHT_CATEGORIES.get(cat_id, {}).get("name", cat_id)
        report += f"| {rank} | {cat_name} | {count:,} |\n"

    report += f"""
---

## Recommendations

Based on the analysis, here are the priority areas:

1. **Address Top Pain Points** - Focus on the most mentioned issues
2. **Improve Stability** - Reduce crashes and bugs
3. **Enhance Connectivity** - WiFi/Bluetooth reliability
4. **Review Subscription Model** - HP+/Instant Ink feedback

---

*Report generated by CustomerInsight_Review_Agent*
"""

    # Save report
    report_path = f"{CONFIG['reports_dir']}/pm_insights_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"💾 Saved: {report_path}")

    return report


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Automated App Store Review Analysis Pipeline")
    parser.add_argument("--scrape", action="store_true", help="Collect latest reviews")
    parser.add_argument("--analyze", action="store_true", help="Run analysis")
    parser.add_argument("--visualize", action="store_true", help="Generate visualizations")
    parser.add_argument("--report", action="store_true", help="Generate PM report")
    parser.add_argument("--all", action="store_true", help="Run full pipeline")

    args = parser.parse_args()

    # Ensure directories exist
    ensure_dirs()

    if args.all or (not any([args.scrape, args.analyze, args.visualize, args.report])):
        # Run full pipeline
        scrape_reviews()
        run_analysis()
        generate_visualizations()
        generate_report()
    else:
        if args.scrape:
            scrape_reviews()
        if args.analyze:
            run_analysis()
        if args.visualize:
            generate_visualizations()
        if args.report:
            generate_report()

    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
