"""
================================================================================
HP App - Full Analysis (October 2025 onwards)
Using CustomerInsight_Review_Agent Framework
US Market - iOS + Google Play
================================================================================
"""

import json
from datetime import datetime
from collections import Counter, defaultdict

# ============================================================================
# CUSTOMERINSIGHT_REVIEW_AGENT CATEGORIES & SENTIMENT
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
# ANALYSIS FUNCTIONS
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
    """Main analysis function using CustomerInsight_Review_Agent framework"""

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
            if len(category_reviews[cat]) < 15:
                category_reviews[cat].append({
                    "rating": rating,
                    "title": title[:50] if title else "",
                    "snippet": content[:250] if content else "",
                    "sentiment": sentiment,
                    "source": source_name,
                    "date": review.get("date", "")[:10]
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
# REPORT GENERATION
# ============================================================================

def generate_report(ios_analysis, gplay_analysis, combined_analysis):
    """Generate comprehensive PM report"""

    report = []

    # Header
    report.append("# HP Smart App - US Market Full Analysis")
    report.append("## October 2025 - January 2026")
    report.append("")
    report.append("---")
    report.append("")
    report.append("**Report Type:** Product Management Customer Insights")
    report.append("**App:** HP Smart")
    report.append("**Markets:** iOS App Store + Google Play Store")
    report.append("**Region:** United States")
    report.append("**Period:** October 2025 - January 2026")
    report.append(f"**Analysis Date:** {datetime.now().strftime('%B %d, %Y')}")
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
    neu_pct = sent["neutral"] / total * 100 if total > 0 else 0

    ios_total = ios_analysis["total_reviews"]
    gplay_total = gplay_analysis["total_reviews"]

    ios_avg = sum(r * c for r, c in ios_analysis['rating_distribution'].items()) / ios_total if ios_total > 0 else 0
    gplay_avg = sum(r * c for r, c in gplay_analysis['rating_distribution'].items()) / gplay_total if gplay_total > 0 else 0
    combined_avg = sum(r * c for r, c in combined_analysis['rating_distribution'].items()) / total if total > 0 else 0

    report.append("### Data Overview")
    report.append("")
    report.append("| Platform | Reviews | Avg Rating | 1-Star % | 5-Star % |")
    report.append("|----------|---------|------------|----------|----------|")

    for analysis, name in [(ios_analysis, "iOS App Store"), (gplay_analysis, "Google Play"), (combined_analysis, "**COMBINED**")]:
        t = analysis["total_reviews"]
        avg = sum(r * c for r, c in analysis['rating_distribution'].items()) / t if t > 0 else 0
        one_star = analysis['rating_distribution'].get(1, 0) / t * 100 if t > 0 else 0
        five_star = analysis['rating_distribution'].get(5, 0) / t * 100 if t > 0 else 0
        report.append(f"| {name} | {t:,} | {avg:.2f} | {one_star:.1f}% | {five_star:.1f}% |")

    report.append("")

    # The Bottom Line
    one_star_pct = combined_analysis['rating_distribution'].get(1, 0) / total * 100
    report.append("### The Bottom Line")
    report.append("")

    if one_star_pct > 60:
        report.append(f"**CRITICAL:** {one_star_pct:.0f}% of US reviews are 1-star ratings. The HP Smart app is experiencing severe user dissatisfaction.")
    elif one_star_pct > 50:
        report.append(f"**SEVERE:** {one_star_pct:.0f}% of US reviews are 1-star ratings. Immediate attention required.")
    elif one_star_pct > 40:
        report.append(f"**WARNING:** {one_star_pct:.0f}% of US reviews are 1-star ratings. User experience needs significant improvement.")
    else:
        report.append(f"**ATTENTION:** {one_star_pct:.0f}% of US reviews are 1-star ratings.")

    report.append("")
    report.append(f"**Sentiment:** {pos_pct:.1f}% Positive | {neg_pct:.1f}% Negative | {neu_pct:.1f}% Neutral")
    report.append("")

    # Rating Distribution
    report.append("---")
    report.append("")
    report.append("## RATING DISTRIBUTION")
    report.append("")

    report.append("### Combined (All Platforms)")
    report.append("")
    report.append("| Rating | Count | Percentage | Visual |")
    report.append("|--------|-------|------------|--------|")

    ratings = combined_analysis["rating_distribution"]
    for r in range(5, 0, -1):
        count = ratings.get(r, 0)
        pct = count / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 3) + "░" * (33 - int(pct / 3))
        stars = "⭐" * r
        report.append(f"| {stars} {r} | {count:,} | {pct:.1f}% | {bar} |")
    report.append("")

    # Sentiment
    report.append("### Sentiment Analysis")
    report.append("")
    report.append("| Sentiment | Count | Percentage |")
    report.append("|-----------|-------|------------|")
    for s in ["positive", "negative", "neutral"]:
        count = sent.get(s, 0)
        pct = count / total * 100 if total > 0 else 0
        emoji = "✅" if s == "positive" else ("❌" if s == "negative" else "➖")
        report.append(f"| {emoji} {s.capitalize()} | {count:,} | {pct:.1f}% |")
    report.append("")

    # Top Issues
    report.append("---")
    report.append("")
    report.append("## TOP 10 CUSTOMER ISSUES")
    report.append("")

    top_categories = combined_analysis["category_counts"].most_common(10)

    report.append("| Rank | Issue | Mentions | % of Reviews | Neg Sent % | Severity | PM Focus |")
    report.append("|------|-------|----------|--------------|------------|----------|----------|")

    for rank, (cat_id, count) in enumerate(top_categories, 1):
        if cat_id == "uncategorized":
            cat_name = "Other/Uncategorized"
            pm_focus = "Manual review"
        else:
            cat_info = INSIGHT_CATEGORIES.get(cat_id, {})
            cat_name = cat_info.get("name", cat_id)
            pm_focus = cat_info.get("pm_focus", "")[:30]

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

        report.append(f"| {rank} | {cat_name} | {count:,} | {pct:.1f}% | {neg_ratio:.0f}% | {severity} | {pm_focus}... |")

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
        report.append(f"**Total Mentions:** {count:,} reviews ({pct:.1f}% of all reviews)")
        report.append(f"**PM Focus:** {pm_focus}")
        report.append("")

        # Sentiment breakdown
        report.append("**Sentiment Breakdown:**")
        report.append("")
        report.append("| Sentiment | Count | % of Category |")
        report.append("|-----------|-------|---------------|")
        for s in ["positive", "negative", "neutral"]:
            s_count = cat_sent.get(s, 0)
            s_pct = s_count / cat_total * 100 if cat_total > 0 else 0
            report.append(f"| {s.capitalize()} | {s_count:,} | {s_pct:.1f}% |")
        report.append("")

        # Sample reviews
        samples = combined_analysis["category_reviews"].get(cat_id, [])
        neg_samples = [s for s in samples if s["sentiment"] == "negative"][:4]
        pos_samples = [s for s in samples if s["sentiment"] == "positive"][:2]

        if neg_samples:
            report.append("**Sample Negative Reviews:**")
            report.append("")
            for sample in neg_samples:
                snippet = sample["snippet"][:200] + "..." if len(sample["snippet"]) > 200 else sample["snippet"]
                report.append(f"> \"{snippet}\"")
                report.append(f"> — {sample['rating']}★ | {sample['source']} | {sample['date']}")
                report.append("")

        if pos_samples:
            report.append("**Sample Positive Reviews:**")
            report.append("")
            for sample in pos_samples:
                snippet = sample["snippet"][:200] + "..." if len(sample["snippet"]) > 200 else sample["snippet"]
                report.append(f"> \"{snippet}\"")
                report.append(f"> — {sample['rating']}★ | {sample['source']} | {sample['date']}")
                report.append("")

        report.append("---")
        report.append("")

    # Platform Comparison
    report.append("## iOS vs ANDROID COMPARISON")
    report.append("")

    report.append("### Rating Comparison")
    report.append("")
    report.append("| Metric | iOS App Store | Google Play |")
    report.append("|--------|---------------|-------------|")
    report.append(f"| Total Reviews | {ios_total:,} | {gplay_total:,} |")
    report.append(f"| Average Rating | {ios_avg:.2f} | {gplay_avg:.2f} |")

    ios_1star = ios_analysis['rating_distribution'].get(1, 0) / ios_total * 100 if ios_total > 0 else 0
    gplay_1star = gplay_analysis['rating_distribution'].get(1, 0) / gplay_total * 100 if gplay_total > 0 else 0
    report.append(f"| 1-Star Reviews | {ios_1star:.1f}% | {gplay_1star:.1f}% |")

    ios_5star = ios_analysis['rating_distribution'].get(5, 0) / ios_total * 100 if ios_total > 0 else 0
    gplay_5star = gplay_analysis['rating_distribution'].get(5, 0) / gplay_total * 100 if gplay_total > 0 else 0
    report.append(f"| 5-Star Reviews | {ios_5star:.1f}% | {gplay_5star:.1f}% |")

    ios_neg = ios_analysis['sentiment_counts'].get('negative', 0) / ios_total * 100 if ios_total > 0 else 0
    gplay_neg = gplay_analysis['sentiment_counts'].get('negative', 0) / gplay_total * 100 if gplay_total > 0 else 0
    report.append(f"| Negative Sentiment | {ios_neg:.1f}% | {gplay_neg:.1f}% |")
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
        report.append(f"| {i+1} | {ios_cat} ({ios_count:,}) | {gplay_cat} ({gplay_count:,}) |")
    report.append("")

    # PM Recommendations
    report.append("---")
    report.append("")
    report.append("## PM RECOMMENDATIONS")
    report.append("")

    recommendations = []

    # Generate based on analysis
    reliability_sent = combined_analysis["category_sentiment"].get("reliability", {})
    reliability_neg = reliability_sent.get("negative", 0) / sum(reliability_sent.values()) * 100 if sum(reliability_sent.values()) > 0 else 0
    if reliability_neg > 50:
        recommendations.append(("CRITICAL", "App Stability", f"Reliability issues have {reliability_neg:.0f}% negative sentiment. Prioritize crash fixes and stability improvements immediately."))

    conn_count = combined_analysis["category_counts"].get("connectivity", 0)
    if conn_count > total * 0.15:
        recommendations.append(("HIGH", "Connectivity", f"Connectivity mentioned in {conn_count:,} reviews ({conn_count/total*100:.1f}%). Implement auto-reconnect and improve setup flow."))

    value_sent = combined_analysis["category_sentiment"].get("value", {})
    value_neg = value_sent.get("negative", 0) / sum(value_sent.values()) * 100 if sum(value_sent.values()) > 0 else 0
    if value_neg > 40:
        recommendations.append(("HIGH", "Pricing/Subscription", f"Value perception is {value_neg:.0f}% negative. Review HP+/Instant Ink messaging and consider friction reduction."))

    if one_star_pct > 60:
        recommendations.append(("CRITICAL", "Overall Experience", f"{one_star_pct:.0f}% 1-star reviews indicates systemic issues. Executive attention required."))

    if gplay_avg < ios_avg - 0.2:
        recommendations.append(("MEDIUM", "Android Focus", f"Android rating ({gplay_avg:.2f}) significantly lower than iOS ({ios_avg:.2f}). Prioritize Android-specific fixes."))

    report.append("| Priority | Area | Recommendation |")
    report.append("|----------|------|----------------|")
    for priority, area, rec in recommendations:
        report.append(f"| **{priority}** | {area} | {rec} |")
    report.append("")

    # Action Plan
    report.append("---")
    report.append("")
    report.append("## PM ACTION PLAN")
    report.append("")
    report.append("### Phase 1: Crisis Response (0-30 days)")
    report.append("- Address top crash/stability issues")
    report.append("- Fix critical connectivity bugs")
    report.append("- Improve error messaging with actionable guidance")
    report.append("- Review and reduce aggressive subscription prompts")
    report.append("")
    report.append("### Phase 2: Core Experience (30-90 days)")
    report.append("- Simplify first-time setup (target: <5 steps)")
    report.append("- Implement reliable auto-reconnect for WiFi")
    report.append("- Add in-app network diagnostics")
    report.append("- Focus on Android-specific issues")
    report.append("")
    report.append("### Phase 3: Rebuild Trust (90-180 days)")
    report.append("- Make HP+ truly optional")
    report.append("- Implement proactive printer health monitoring")
    report.append("- Launch customer feedback program")
    report.append("- Target 3.5+ average rating")
    report.append("")

    # Footer
    report.append("---")
    report.append("")
    report.append("*Report Generated by CustomerInsight_Review_Agent v1.1*")
    report.append(f"*Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    report.append(f"*Data: {total:,} reviews from US Market (iOS: {ios_total:,}, Android: {gplay_total:,})*")
    report.append("*Period: October 2025 - January 2026*")

    return "\n".join(report)


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("HP APP - FULL ANALYSIS (October 2025+)")
    print("Using CustomerInsight_Review_Agent Framework")
    print("="*70)

    # Load iOS reviews
    print("\nLoading iOS App Store reviews...")
    try:
        with open("HP_App_iOS_US_Oct2025_Full.json", "r") as f:
            ios_reviews = json.load(f)
        print(f"  Loaded: {len(ios_reviews)} iOS reviews")
    except FileNotFoundError:
        print("  iOS data file not found, using existing data...")
        with open("HP_app.json", "r") as f:
            all_ios = json.load(f)
        ios_reviews = [r for r in all_ios if r.get("country") == "us"]
        print(f"  Loaded: {len(ios_reviews)} iOS US reviews")

    # Load Google Play reviews
    print("\nLoading Google Play reviews...")
    try:
        with open("HP_App_GooglePlay_US_Oct2025_Full.json", "r") as f:
            gplay_reviews = json.load(f)
        print(f"  Loaded: {len(gplay_reviews)} Google Play reviews")
    except FileNotFoundError:
        print("  Google Play data file not found!")
        gplay_reviews = []

    # Analyze
    print("\nAnalyzing iOS reviews...")
    ios_analysis = analyze_reviews(ios_reviews, "iOS App Store")

    print("Analyzing Google Play reviews...")
    gplay_analysis = analyze_reviews(gplay_reviews, "Google Play")

    print("Creating combined analysis...")
    combined_reviews = ios_reviews + gplay_reviews
    combined_analysis = analyze_reviews(combined_reviews, "Combined")

    # Generate report
    print("\nGenerating PM Insights Report...")
    report = generate_report(ios_analysis, gplay_analysis, combined_analysis)

    # Save report
    with open("HP_App_US_Full_Insights_Oct2025.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ Saved: HP_App_US_Full_Insights_Oct2025.md")

    # Save JSON data
    json_output = {
        "report_info": {
            "title": "HP App - US Market Full Analysis",
            "period": "October 2025 - January 2026",
            "region": "United States",
            "analysis_date": datetime.now().isoformat(),
            "agent": "CustomerInsight_Review_Agent v1.1"
        },
        "summary": {
            "total_reviews": combined_analysis["total_reviews"],
            "ios_reviews": ios_analysis["total_reviews"],
            "gplay_reviews": gplay_analysis["total_reviews"],
            "combined_avg_rating": round(sum(r * c for r, c in combined_analysis['rating_distribution'].items()) / combined_analysis["total_reviews"], 2) if combined_analysis["total_reviews"] > 0 else 0,
            "ios_avg_rating": round(sum(r * c for r, c in ios_analysis['rating_distribution'].items()) / ios_analysis["total_reviews"], 2) if ios_analysis["total_reviews"] > 0 else 0,
            "gplay_avg_rating": round(sum(r * c for r, c in gplay_analysis['rating_distribution'].items()) / gplay_analysis["total_reviews"], 2) if gplay_analysis["total_reviews"] > 0 else 0,
        },
        "sentiment": {
            "positive": combined_analysis["sentiment_counts"]["positive"],
            "negative": combined_analysis["sentiment_counts"]["negative"],
            "neutral": combined_analysis["sentiment_counts"]["neutral"],
        },
        "rating_distribution": dict(combined_analysis["rating_distribution"]),
        "top_issues": [
            {
                "rank": rank,
                "category_id": cat_id,
                "name": INSIGHT_CATEGORIES.get(cat_id, {}).get("name", cat_id),
                "mention_count": count,
                "percentage": round(count / combined_analysis["total_reviews"] * 100, 1),
                "sentiment": combined_analysis["category_sentiment"].get(cat_id, {}),
                "sample_reviews": combined_analysis["category_reviews"].get(cat_id, [])[:5]
            }
            for rank, (cat_id, count) in enumerate(combined_analysis["category_counts"].most_common(10), 1)
        ],
        "ios_analysis": {
            "total": ios_analysis["total_reviews"],
            "sentiment": dict(ios_analysis["sentiment_counts"]),
            "rating_distribution": dict(ios_analysis["rating_distribution"]),
            "top_categories": [(cat, count) for cat, count in ios_analysis["category_counts"].most_common(5)]
        },
        "gplay_analysis": {
            "total": gplay_analysis["total_reviews"],
            "sentiment": dict(gplay_analysis["sentiment_counts"]),
            "rating_distribution": dict(gplay_analysis["rating_distribution"]),
            "top_categories": [(cat, count) for cat, count in gplay_analysis["category_counts"].most_common(5)]
        }
    }

    with open("HP_App_US_Full_Insights_Oct2025.json", "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print("✅ Saved: HP_App_US_Full_Insights_Oct2025.json")

    # Print Summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

    total = combined_analysis["total_reviews"]
    combined_avg = sum(r * c for r, c in combined_analysis['rating_distribution'].items()) / total if total > 0 else 0
    neg_pct = combined_analysis["sentiment_counts"]["negative"] / total * 100

    top_cats = combined_analysis["category_counts"].most_common(3)

    print(f"""
DATA SUMMARY:
  iOS App Store:     {ios_analysis['total_reviews']:,} reviews
  Google Play:       {gplay_analysis['total_reviews']:,} reviews
  ────────────────────────────────
  TOTAL:             {total:,} reviews

RATINGS:
  Combined Average:  {combined_avg:.2f} / 5.0
  1-Star Reviews:    {combined_analysis['rating_distribution'].get(1, 0):,} ({combined_analysis['rating_distribution'].get(1, 0)/total*100:.1f}%)
  5-Star Reviews:    {combined_analysis['rating_distribution'].get(5, 0):,} ({combined_analysis['rating_distribution'].get(5, 0)/total*100:.1f}%)

SENTIMENT:
  Positive:          {combined_analysis['sentiment_counts']['positive']:,} ({combined_analysis['sentiment_counts']['positive']/total*100:.1f}%)
  Negative:          {combined_analysis['sentiment_counts']['negative']:,} ({neg_pct:.1f}%)
  Neutral:           {combined_analysis['sentiment_counts']['neutral']:,} ({combined_analysis['sentiment_counts']['neutral']/total*100:.1f}%)

TOP 3 ISSUES:
  1. {INSIGHT_CATEGORIES.get(top_cats[0][0], {}).get('name', top_cats[0][0])} ({top_cats[0][1]:,} mentions)
  2. {INSIGHT_CATEGORIES.get(top_cats[1][0], {}).get('name', top_cats[1][0])} ({top_cats[1][1]:,} mentions)
  3. {INSIGHT_CATEGORIES.get(top_cats[2][0], {}).get('name', top_cats[2][0])} ({top_cats[2][1]:,} mentions)

FILES GENERATED:
  - HP_App_US_Full_Insights_Oct2025.md
  - HP_App_US_Full_Insights_Oct2025.json
""")


if __name__ == "__main__":
    main()
