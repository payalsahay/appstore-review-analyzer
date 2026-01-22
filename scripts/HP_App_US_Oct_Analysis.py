"""
================================================================================
HP App - US Market Analysis (October 2025+)
iOS App Store + Google Play Store Combined Analysis
Using CustomerInsight_Review_Agent Framework
================================================================================
"""

import json
from datetime import datetime
from collections import Counter, defaultdict

# ============================================================================
# CUSTOMERINSIGHT_REVIEW_AGENT CATEGORIES & SENTIMENT (from your agent)
# ============================================================================

INSIGHT_CATEGORIES = {
    "connectivity": {
        "name": "Connectivity & Setup",
        "description": "WiFi connection, Bluetooth, network setup, printer discovery",
        "keywords": [
            "wifi", "wi-fi", "connect", "connection", "network", "bluetooth",
            "setup", "find printer", "discover", "pair", "pairing", "wireless",
            "reconnect", "disconnect", "offline", "online", "ip address", "router"
        ],
        "pm_focus": "First-time user experience, connectivity reliability"
    },
    "printing": {
        "name": "Print Quality & Functionality",
        "description": "Print quality, speed, paper handling, print jobs",
        "keywords": [
            "print", "printing", "quality", "resolution", "color", "black and white",
            "b&w", "pages", "paper", "ink", "toner", "cartridge", "jam", "duplex",
            "double-sided", "borderless", "photo", "document", "pdf"
        ],
        "pm_focus": "Core value proposition, print reliability"
    },
    "scanning": {
        "name": "Scanning Features",
        "description": "Scan quality, OCR, scan-to-email, document scanning",
        "keywords": [
            "scan", "scanning", "scanner", "ocr", "document", "scan to email",
            "scan to cloud", "image", "resolution", "quality", "pdf scan"
        ],
        "pm_focus": "Secondary feature adoption, scan workflow"
    },
    "mobile_experience": {
        "name": "Mobile App Experience",
        "description": "App usability, UI/UX, navigation, responsiveness",
        "keywords": [
            "app", "interface", "ui", "ux", "easy", "difficult", "confusing",
            "intuitive", "simple", "complicated", "navigate", "menu", "button",
            "screen", "layout", "design", "user friendly", "responsive"
        ],
        "pm_focus": "App usability, user satisfaction"
    },
    "reliability": {
        "name": "App Reliability & Stability",
        "description": "Crashes, bugs, freezing, performance issues",
        "keywords": [
            "crash", "bug", "freeze", "frozen", "stuck", "error", "fail",
            "not working", "doesn't work", "broken", "glitch", "slow",
            "lag", "hang", "unresponsive", "force close", "restart"
        ],
        "pm_focus": "Technical debt, app stability metrics"
    },
    "updates": {
        "name": "Updates & Compatibility",
        "description": "App updates, iOS/Android compatibility, version issues",
        "keywords": [
            "update", "version", "ios", "iphone", "ipad", "android", "compatible",
            "compatibility", "upgrade", "new version", "old version",
            "after update", "latest", "outdated", "support"
        ],
        "pm_focus": "Release management, OS compatibility"
    },
    "features": {
        "name": "Feature Requests & Missing Features",
        "description": "Desired features, missing functionality, enhancements",
        "keywords": [
            "wish", "want", "need", "should", "could", "would be nice",
            "missing", "add", "feature", "option", "functionality", "ability",
            "please add", "hope", "request", "suggest", "improvement"
        ],
        "pm_focus": "Product roadmap, feature prioritization"
    },
    "account_cloud": {
        "name": "Account & Cloud Services",
        "description": "Login, account management, cloud printing, storage",
        "keywords": [
            "login", "sign in", "account", "password", "register", "cloud",
            "google drive", "dropbox", "icloud", "email", "storage", "sync",
            "authentication", "credentials"
        ],
        "pm_focus": "Account funnel, cloud integration"
    },
    "support": {
        "name": "Customer Support & Help",
        "description": "Support experience, documentation, troubleshooting",
        "keywords": [
            "support", "help", "customer service", "contact", "call",
            "troubleshoot", "guide", "manual", "instructions", "tutorial",
            "faq", "documentation", "assistance"
        ],
        "pm_focus": "Support deflection, self-service success"
    },
    "value": {
        "name": "Value & Pricing",
        "description": "Free vs paid, subscriptions, in-app purchases, worth",
        "keywords": [
            "free", "paid", "subscription", "purchase", "buy", "cost",
            "price", "worth", "value", "money", "expensive", "cheap",
            "ads", "advertisement", "premium", "pro", "instant ink", "hp+"
        ],
        "pm_focus": "Monetization, value perception"
    }
}

SENTIMENT_KEYWORDS = {
    "positive": [
        "love", "great", "excellent", "amazing", "awesome", "perfect",
        "best", "fantastic", "wonderful", "easy", "simple", "works great",
        "highly recommend", "good", "nice", "helpful", "brilliant", "superb",
        "impressed", "satisfied", "reliable", "seamless", "smooth", "fast"
    ],
    "negative": [
        "hate", "terrible", "awful", "worst", "horrible", "bad", "poor",
        "useless", "waste", "frustrating", "annoying", "disappointing",
        "doesn't work", "not working", "broken", "fail", "crash", "bug",
        "difficult", "complicated", "confusing", "slow", "unreliable",
        "garbage", "trash", "ridiculous", "pathetic", "disaster"
    ],
    "neutral": [
        "okay", "ok", "average", "decent", "fine", "works", "basic",
        "standard", "normal", "acceptable"
    ]
}

# ============================================================================
# LOAD AND FILTER DATA
# ============================================================================

def load_and_filter_reviews(filepath, country_filter="us", start_date="2025-10-01"):
    """Load reviews and filter by country and date"""
    with open(filepath, "r", encoding="utf-8") as f:
        all_reviews = json.load(f)

    filtered = []
    start_dt = datetime.fromisoformat(start_date)

    for review in all_reviews:
        # Filter by country
        if review.get("country", "").lower() != country_filter.lower():
            continue

        # Filter by date
        date_str = review.get("date", "")
        if date_str:
            try:
                # Handle different date formats
                date_str_clean = date_str.replace("Z", "+00:00")
                if "T" in date_str_clean:
                    review_date = datetime.fromisoformat(date_str_clean.split("+")[0].split("-07:00")[0])
                else:
                    review_date = datetime.strptime(date_str_clean[:10], "%Y-%m-%d")

                if review_date >= start_dt:
                    filtered.append(review)
            except Exception as e:
                pass  # Skip reviews with invalid dates

    return filtered

# ============================================================================
# ANALYSIS FUNCTIONS (from CustomerInsight_Review_Agent)
# ============================================================================

def analyze_sentiment(text):
    """Analyze sentiment of review text"""
    text_lower = text.lower()

    pos_count = sum(1 for word in SENTIMENT_KEYWORDS["positive"] if word in text_lower)
    neg_count = sum(1 for word in SENTIMENT_KEYWORDS["negative"] if word in text_lower)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

def categorize_review(text):
    """Categorize review into insight categories"""
    text_lower = text.lower()
    categories = []

    for cat_id, cat_info in INSIGHT_CATEGORIES.items():
        for keyword in cat_info["keywords"]:
            if keyword in text_lower:
                categories.append(cat_id)
                break

    return categories if categories else ["uncategorized"]

def analyze_reviews(reviews, source_name):
    """Main analysis function"""

    category_counts = Counter()
    category_sentiment = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
    category_reviews = defaultdict(list)
    sentiment_counts = Counter()
    rating_distribution = Counter()

    for review in reviews:
        content = review.get("content", "") or review.get("review", "") or ""
        title = review.get("title", "") or ""
        full_text = f"{title} {content}"

        rating = int(review.get("rating", 3))
        rating_distribution[rating] += 1

        sentiment = analyze_sentiment(full_text)
        sentiment_counts[sentiment] += 1

        categories = categorize_review(full_text)
        for cat in categories:
            category_counts[cat] += 1
            category_sentiment[cat][sentiment] += 1
            if len(category_reviews[cat]) < 10:
                category_reviews[cat].append({
                    "rating": rating,
                    "title": title[:50] if title else "",
                    "snippet": content[:200] if content else "",
                    "sentiment": sentiment,
                    "source": source_name
                })

    return {
        "source": source_name,
        "total_reviews": len(reviews),
        "category_counts": category_counts,
        "category_sentiment": dict(category_sentiment),
        "category_reviews": dict(category_reviews),
        "sentiment_counts": sentiment_counts,
        "rating_distribution": rating_distribution
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

print("="*70)
print("HP APP - US MARKET ANALYSIS (October 2025 onwards)")
print("Using CustomerInsight_Review_Agent Framework")
print("="*70)

# Load iOS App Store reviews
print("\nLoading iOS App Store reviews...")
ios_reviews = load_and_filter_reviews("HP_app.json", "us", "2025-10-01")
print(f"  iOS US reviews (Oct 2025+): {len(ios_reviews)}")

# Load Google Play reviews
print("Loading Google Play Store reviews...")
gplay_reviews = load_and_filter_reviews("GooglePlay_HP_app.json", "us", "2025-10-01")
print(f"  Google Play US reviews (Oct 2025+): {len(gplay_reviews)}")

# Analyze each
print("\nAnalyzing iOS App Store reviews...")
ios_analysis = analyze_reviews(ios_reviews, "iOS App Store")

print("Analyzing Google Play Store reviews...")
gplay_analysis = analyze_reviews(gplay_reviews, "Google Play")

# Combined analysis
print("Creating combined analysis...")
combined_reviews = ios_reviews + gplay_reviews
combined_analysis = analyze_reviews(combined_reviews, "Combined (iOS + Android)")

# ============================================================================
# GENERATE PM REPORT
# ============================================================================

report = []
report.append("# HP App - US Market Customer Insights Report")
report.append("## October 2025 - January 2026")
report.append("")
report.append("---")
report.append("")
report.append("**Report Type:** Product Management Customer Insights")
report.append("**App:** HP Smart")
report.append("**Markets:** iOS App Store + Google Play Store")
report.append("**Region:** United States Only")
report.append("**Period:** October 2025 onwards")
report.append(f"**Analysis Date:** {datetime.now().strftime('%B %Y')}")
report.append("**Prepared By:** CustomerInsight_Review_Agent v1.1")
report.append("")
report.append("---")
report.append("")

# Executive Summary
report.append("## EXECUTIVE SUMMARY")
report.append("")

total = combined_analysis["total_reviews"]
sent = combined_analysis["sentiment_counts"]
pos_pct = sent["positive"] / total * 100 if total > 0 else 0
neg_pct = sent["negative"] / total * 100 if total > 0 else 0

report.append("### Key Metrics")
report.append("")
report.append("| Metric | iOS App Store | Google Play | Combined |")
report.append("|--------|---------------|-------------|----------|")
report.append(f"| Total Reviews | {ios_analysis['total_reviews']} | {gplay_analysis['total_reviews']} | {total} |")

ios_avg = sum(r * c for r, c in ios_analysis['rating_distribution'].items()) / ios_analysis['total_reviews'] if ios_analysis['total_reviews'] > 0 else 0
gplay_avg = sum(r * c for r, c in gplay_analysis['rating_distribution'].items()) / gplay_analysis['total_reviews'] if gplay_analysis['total_reviews'] > 0 else 0
combined_avg = sum(r * c for r, c in combined_analysis['rating_distribution'].items()) / total if total > 0 else 0

report.append(f"| Average Rating | {ios_avg:.2f} | {gplay_avg:.2f} | {combined_avg:.2f} |")

ios_neg = ios_analysis['sentiment_counts']['negative'] / ios_analysis['total_reviews'] * 100 if ios_analysis['total_reviews'] > 0 else 0
gplay_neg = gplay_analysis['sentiment_counts']['negative'] / gplay_analysis['total_reviews'] * 100 if gplay_analysis['total_reviews'] > 0 else 0

report.append(f"| Negative Sentiment | {ios_neg:.1f}% | {gplay_neg:.1f}% | {neg_pct:.1f}% |")
report.append("")

# Bottom line
report.append("### The Bottom Line")
report.append("")
if neg_pct > 40:
    report.append(f"**CRITICAL:** {neg_pct:.0f}% of US reviews express negative sentiment. The HP Smart app is facing significant user dissatisfaction in the US market.")
elif neg_pct > 25:
    report.append(f"**WARNING:** {neg_pct:.0f}% of US reviews express negative sentiment. User experience needs improvement.")
else:
    report.append(f"**STABLE:** {neg_pct:.0f}% negative sentiment indicates moderate user satisfaction.")
report.append("")

# Rating Distribution
report.append("---")
report.append("")
report.append("## RATING DISTRIBUTION")
report.append("")
report.append("### Combined (iOS + Android)")
report.append("")
report.append("| Rating | Count | Percentage | Visual |")
report.append("|--------|-------|------------|--------|")

ratings = combined_analysis["rating_distribution"]
for r in range(5, 0, -1):
    count = ratings.get(r, 0)
    pct = count / total * 100 if total > 0 else 0
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    stars = "⭐" * r
    report.append(f"| {stars} {r} stars | {count} | {pct:.1f}% | {bar} |")
report.append("")

# Sentiment Overview
report.append("### Sentiment Overview")
report.append("")
report.append("| Sentiment | Count | Percentage |")
report.append("|-----------|-------|------------|")
for s in ["positive", "negative", "neutral"]:
    count = sent.get(s, 0)
    pct = count / total * 100 if total > 0 else 0
    report.append(f"| {s.capitalize()} | {count} | {pct:.1f}% |")
report.append("")

# Top Issues
report.append("---")
report.append("")
report.append("## TOP 10 CUSTOMER ISSUES")
report.append("")
report.append("### Priority Ranking (Combined iOS + Android)")
report.append("")

top_categories = combined_analysis["category_counts"].most_common(10)

report.append("| Rank | Issue | Mentions | % of Reviews | Neg % | Severity | PM Focus |")
report.append("|------|-------|----------|--------------|-------|----------|----------|")

for rank, (cat_id, count) in enumerate(top_categories, 1):
    if cat_id == "uncategorized":
        cat_name = "Other/Uncategorized"
        pm_focus = "Manual review"
    else:
        cat_info = INSIGHT_CATEGORIES.get(cat_id, {})
        cat_name = cat_info.get("name", cat_id)
        pm_focus = cat_info.get("pm_focus", "")

    pct = count / total * 100 if total > 0 else 0

    cat_sent = combined_analysis["category_sentiment"].get(cat_id, {})
    cat_total = sum(cat_sent.values())
    neg_ratio = cat_sent.get("negative", 0) / cat_total * 100 if cat_total > 0 else 0

    if neg_ratio > 60:
        severity = "🔴 Critical"
    elif neg_ratio > 40:
        severity = "🟠 High"
    elif neg_ratio > 25:
        severity = "🟡 Medium"
    else:
        severity = "🟢 Low"

    report.append(f"| {rank} | {cat_name} | {count} | {pct:.1f}% | {neg_ratio:.0f}% | {severity} | {pm_focus[:30]}... |")

report.append("")

# Detailed Issue Analysis
report.append("---")
report.append("")
report.append("## DETAILED ISSUE ANALYSIS")
report.append("")

for rank, (cat_id, count) in enumerate(top_categories[:5], 1):
    if cat_id == "uncategorized":
        continue

    cat_info = INSIGHT_CATEGORIES.get(cat_id, {})
    cat_name = cat_info.get("name", cat_id)
    cat_desc = cat_info.get("description", "")
    pm_focus = cat_info.get("pm_focus", "")

    pct = count / total * 100 if total > 0 else 0

    cat_sent = combined_analysis["category_sentiment"].get(cat_id, {})
    cat_total = sum(cat_sent.values())

    report.append(f"### {rank}. {cat_name}")
    report.append("")
    report.append(f"**Description:** {cat_desc}")
    report.append(f"**Mentions:** {count} reviews ({pct:.1f}%)")
    report.append(f"**PM Focus:** {pm_focus}")
    report.append("")

    # Sentiment breakdown
    report.append("**Sentiment Breakdown:**")
    report.append("")
    report.append("| Sentiment | Count | Percentage |")
    report.append("|-----------|-------|------------|")
    for s in ["positive", "negative", "neutral"]:
        s_count = cat_sent.get(s, 0)
        s_pct = s_count / cat_total * 100 if cat_total > 0 else 0
        report.append(f"| {s.capitalize()} | {s_count} | {s_pct:.1f}% |")
    report.append("")

    # Sample reviews
    samples = combined_analysis["category_reviews"].get(cat_id, [])
    neg_samples = [s for s in samples if s["sentiment"] == "negative"][:3]
    pos_samples = [s for s in samples if s["sentiment"] == "positive"][:2]

    if neg_samples:
        report.append("**Sample Negative Feedback:**")
        report.append("")
        for sample in neg_samples:
            snippet = sample["snippet"][:150] + "..." if len(sample["snippet"]) > 150 else sample["snippet"]
            report.append(f"> \"{snippet}\" — {sample['rating']}★ ({sample['source']})")
            report.append("")

    if pos_samples:
        report.append("**Sample Positive Feedback:**")
        report.append("")
        for sample in pos_samples:
            snippet = sample["snippet"][:150] + "..." if len(sample["snippet"]) > 150 else sample["snippet"]
            report.append(f"> \"{snippet}\" — {sample['rating']}★ ({sample['source']})")
            report.append("")

    report.append("---")
    report.append("")

# iOS vs Android Comparison
report.append("## iOS vs ANDROID COMPARISON")
report.append("")
report.append("### Top Issues by Platform")
report.append("")

ios_top = ios_analysis["category_counts"].most_common(5)
gplay_top = gplay_analysis["category_counts"].most_common(5)

report.append("| Rank | iOS App Store | Google Play |")
report.append("|------|---------------|-------------|")
for i in range(5):
    ios_cat = INSIGHT_CATEGORIES.get(ios_top[i][0], {}).get("name", ios_top[i][0]) if i < len(ios_top) else "-"
    gplay_cat = INSIGHT_CATEGORIES.get(gplay_top[i][0], {}).get("name", gplay_top[i][0]) if i < len(gplay_top) else "-"
    ios_count = ios_top[i][1] if i < len(ios_top) else 0
    gplay_count = gplay_top[i][1] if i < len(gplay_top) else 0
    report.append(f"| {i+1} | {ios_cat} ({ios_count}) | {gplay_cat} ({gplay_count}) |")
report.append("")

# PM Recommendations
report.append("---")
report.append("")
report.append("## PM RECOMMENDATIONS")
report.append("")

recommendations = []

# Generate recommendations based on analysis
conn_count = combined_analysis["category_counts"].get("connectivity", 0)
if conn_count > total * 0.15:
    recommendations.append(("PRIORITY", "Connectivity & Setup", "WiFi/Bluetooth connectivity is the #1 pain point. Implement auto-reconnect and improve first-time setup flow."))

rel_count = combined_analysis["category_counts"].get("reliability", 0)
if rel_count > total * 0.1:
    recommendations.append(("HIGH", "App Stability", "Address app crashes and bugs. Implement crash reporting and prioritize stability sprint."))

val_count = combined_analysis["category_counts"].get("value", 0)
val_sent = combined_analysis["category_sentiment"].get("value", {})
if val_count > 0 and val_sent.get("negative", 0) / val_count > 0.5:
    recommendations.append(("HIGH", "Subscription Model", "Subscription/Instant Ink complaints are high. Consider making HP+ truly optional and reduce upsell friction."))

upd_count = combined_analysis["category_counts"].get("updates", 0)
if upd_count > total * 0.08:
    recommendations.append(("MEDIUM", "Update Quality", "Users report issues after updates. Improve QA process and consider staged rollouts."))

if neg_pct > 40:
    recommendations.append(("CRITICAL", "Overall Experience", f"With {neg_pct:.0f}% negative sentiment, immediate action required across all fronts."))

report.append("| Priority | Area | Recommendation |")
report.append("|----------|------|----------------|")
for priority, area, rec in recommendations:
    report.append(f"| {priority} | {area} | {rec} |")
report.append("")

# Action Plan
report.append("---")
report.append("")
report.append("## PM ACTION PLAN")
report.append("")
report.append("### Phase 1: Stabilization (0-30 days)")
report.append("- Fix top crash scenarios identified in reviews")
report.append("- Improve WiFi reconnection reliability")
report.append("- Reduce subscription prompts in critical user flows")
report.append("")
report.append("### Phase 2: Core Experience (30-90 days)")
report.append("- Simplify first-time setup to 5 steps or less")
report.append("- Add network diagnostic tool in app")
report.append("- Improve error messages with actionable guidance")
report.append("")
report.append("### Phase 3: Delight (90-180 days)")
report.append("- Make HP+ truly optional without degraded experience")
report.append("- Add user-requested features from positive feedback")
report.append("- Implement proactive printer health monitoring")
report.append("")

# Footer
report.append("---")
report.append("")
report.append("*Report Generated by CustomerInsight_Review_Agent v1.1*")
report.append(f"*Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
report.append("*Data Sources: iOS App Store + Google Play Store - US Market Only*")

# ============================================================================
# SAVE OUTPUTS
# ============================================================================

# Save report
report_content = "\n".join(report)
with open("HP_App_US_Oct_Insights.md", "w", encoding="utf-8") as f:
    f.write(report_content)
print(f"\n✅ Saved: HP_App_US_Oct_Insights.md")

# Save JSON data
json_output = {
    "report_info": {
        "title": "HP App - US Market Customer Insights",
        "period": "October 2025 onwards",
        "region": "United States",
        "platforms": ["iOS App Store", "Google Play Store"],
        "analysis_date": datetime.now().isoformat(),
        "agent": "CustomerInsight_Review_Agent v1.1"
    },
    "summary": {
        "total_reviews": total,
        "ios_reviews": ios_analysis["total_reviews"],
        "gplay_reviews": gplay_analysis["total_reviews"],
        "average_rating": round(combined_avg, 2),
        "ios_average_rating": round(ios_avg, 2),
        "gplay_average_rating": round(gplay_avg, 2),
        "sentiment": {
            "positive_pct": round(pos_pct, 1),
            "negative_pct": round(neg_pct, 1),
            "neutral_pct": round(100 - pos_pct - neg_pct, 1)
        }
    },
    "rating_distribution": dict(combined_analysis["rating_distribution"]),
    "top_issues": [
        {
            "rank": rank,
            "category_id": cat_id,
            "name": INSIGHT_CATEGORIES.get(cat_id, {}).get("name", cat_id),
            "mention_count": count,
            "percentage": round(count / total * 100, 1),
            "sentiment": combined_analysis["category_sentiment"].get(cat_id, {}),
            "pm_focus": INSIGHT_CATEGORIES.get(cat_id, {}).get("pm_focus", ""),
            "sample_reviews": combined_analysis["category_reviews"].get(cat_id, [])[:5]
        }
        for rank, (cat_id, count) in enumerate(top_categories[:10], 1)
    ],
    "ios_analysis": {
        "total": ios_analysis["total_reviews"],
        "sentiment": dict(ios_analysis["sentiment_counts"]),
        "top_categories": [(cat, count) for cat, count in ios_analysis["category_counts"].most_common(5)]
    },
    "gplay_analysis": {
        "total": gplay_analysis["total_reviews"],
        "sentiment": dict(gplay_analysis["sentiment_counts"]),
        "top_categories": [(cat, count) for cat, count in gplay_analysis["category_counts"].most_common(5)]
    }
}

with open("HP_App_US_Oct_Insights.json", "w", encoding="utf-8") as f:
    json.dump(json_output, f, indent=2, ensure_ascii=False)
print(f"✅ Saved: HP_App_US_Oct_Insights.json")

# Save filtered reviews
with open("HP_App_US_Oct_iOS_Reviews.json", "w", encoding="utf-8") as f:
    json.dump(ios_reviews, f, indent=2, ensure_ascii=False, default=str)
print(f"✅ Saved: HP_App_US_Oct_iOS_Reviews.json ({len(ios_reviews)} reviews)")

with open("HP_App_US_Oct_GooglePlay_Reviews.json", "w", encoding="utf-8") as f:
    json.dump(gplay_reviews, f, indent=2, ensure_ascii=False, default=str)
print(f"✅ Saved: HP_App_US_Oct_GooglePlay_Reviews.json ({len(gplay_reviews)} reviews)")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)

# Print summary
print(f"""
SUMMARY:
  iOS App Store (US, Oct 2025+):    {ios_analysis['total_reviews']} reviews, Avg: {ios_avg:.2f}
  Google Play (US, Oct 2025+):      {gplay_analysis['total_reviews']} reviews, Avg: {gplay_avg:.2f}
  Combined:                         {total} reviews, Avg: {combined_avg:.2f}

  Sentiment: {pos_pct:.1f}% Positive | {neg_pct:.1f}% Negative

  Top 3 Issues:
    1. {INSIGHT_CATEGORIES.get(top_categories[0][0], {}).get('name', top_categories[0][0])} ({top_categories[0][1]} mentions)
    2. {INSIGHT_CATEGORIES.get(top_categories[1][0], {}).get('name', top_categories[1][0])} ({top_categories[1][1]} mentions)
    3. {INSIGHT_CATEGORIES.get(top_categories[2][0], {}).get('name', top_categories[2][0])} ({top_categories[2][1]} mentions)
""")
