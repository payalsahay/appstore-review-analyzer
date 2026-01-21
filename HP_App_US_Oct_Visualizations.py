"""
================================================================================
HP App - US Market Visualizations (October 2025+)
Executive Dashboard + Separate Platform Analysis
================================================================================
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.titleweight'] = 'bold'

# Load data
with open("HP_App_US_Oct_Insights.json", "r") as f:
    data = json.load(f)

# ============================================================================
# 1. EXECUTIVE DASHBOARD (Combined)
# ============================================================================

def create_executive_dashboard():
    """Create executive summary dashboard for combined iOS + Android"""

    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor('#f8f9fa')

    # Title
    fig.suptitle('HP Smart App - US Market Executive Dashboard\nOctober 2025 - January 2026 | iOS App Store + Google Play',
                 fontsize=18, fontweight='bold', y=0.98, color='#2c3e50')

    gs = GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3,
                  left=0.05, right=0.95, top=0.90, bottom=0.05)

    # Colors
    hp_blue = '#0096D6'
    hp_dark = '#2c3e50'
    colors_rating = ['#27ae60', '#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
    colors_sentiment = ['#27ae60', '#e74c3c', '#95a5a6']
    colors_issues = ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#9b59b6',
                     '#1abc9c', '#34495e', '#16a085', '#2980b9', '#8e44ad']

    # =========================================================================
    # ROW 1: Key Metrics
    # =========================================================================

    ax_metrics = fig.add_subplot(gs[0, :])
    ax_metrics.axis('off')
    ax_metrics.set_xlim(0, 1)
    ax_metrics.set_ylim(0, 1)

    metrics = [
        (f"{data['summary']['total_reviews']:,}", "Total Reviews", hp_blue, "US Market"),
        (f"{data['summary']['average_rating']:.2f}/5.0", "Average Rating", '#e74c3c', "Combined"),
        (f"{data['summary']['sentiment']['negative_pct']}%", "Negative Sentiment", '#c0392b', "Warning"),
        (f"57.7%", "1-Star Reviews", '#e74c3c', "Critical"),
        (f"{data['summary']['ios_reviews']}", "iOS Reviews", '#555', "App Store"),
        (f"{data['summary']['gplay_reviews']}", "Android Reviews", '#3ddc84', "Google Play"),
    ]

    box_width = 0.14
    start_x = 0.04

    for i, (value, label, color, sublabel) in enumerate(metrics):
        x = start_x + i * 0.16

        # Box background
        rect = mpatches.FancyBboxPatch((x, 0.15), box_width, 0.7,
                                        boxstyle="round,pad=0.02,rounding_size=0.02",
                                        facecolor='white', edgecolor=color,
                                        linewidth=3, transform=ax_metrics.transAxes)
        ax_metrics.add_patch(rect)

        # Value
        ax_metrics.text(x + box_width/2, 0.58, value, fontsize=22, fontweight='bold',
                       ha='center', va='center', color=color, transform=ax_metrics.transAxes)
        # Label
        ax_metrics.text(x + box_width/2, 0.35, label, fontsize=11, fontweight='bold',
                       ha='center', va='center', color='#333', transform=ax_metrics.transAxes)
        # Sublabel
        ax_metrics.text(x + box_width/2, 0.22, sublabel, fontsize=9,
                       ha='center', va='center', color='#777', transform=ax_metrics.transAxes)

    # =========================================================================
    # ROW 2: Rating Distribution + Sentiment + Platform Comparison
    # =========================================================================

    # Rating Distribution (Combined)
    ax_rating = fig.add_subplot(gs[1, 0:2])

    rating_dist = data['rating_distribution']
    stars = ['5★', '4★', '3★', '2★', '1★']
    counts = [rating_dist.get(str(5-i), 0) for i in range(5)]
    total = sum(counts)
    percentages = [c/total*100 for c in counts]

    bars = ax_rating.barh(stars, percentages, color=colors_rating, edgecolor='white', height=0.6)

    for bar, pct, count in zip(bars, percentages, counts):
        width = bar.get_width()
        ax_rating.text(width + 1.5, bar.get_y() + bar.get_height()/2,
                      f'{pct:.1f}% ({count})', va='center', fontsize=10, fontweight='bold')

    ax_rating.set_xlabel('Percentage of Reviews', fontsize=11)
    ax_rating.set_title('Rating Distribution (Combined)', fontsize=13, fontweight='bold', pad=10)
    ax_rating.set_xlim(0, 75)
    ax_rating.spines['top'].set_visible(False)
    ax_rating.spines['right'].set_visible(False)

    # Sentiment Pie Chart
    ax_sentiment = fig.add_subplot(gs[1, 2])

    sentiment = data['summary']['sentiment']
    sizes = [sentiment['positive_pct'], sentiment['negative_pct'], sentiment['neutral_pct']]
    labels = ['Positive\n26.9%', 'Negative\n28.9%', 'Neutral\n44.2%']
    explode = (0, 0.05, 0)

    wedges, texts = ax_sentiment.pie(sizes, colors=colors_sentiment, explode=explode,
                                      startangle=90, wedgeprops=dict(width=0.7, edgecolor='white'))

    ax_sentiment.legend(wedges, labels, loc='center', fontsize=10, frameon=False)
    ax_sentiment.set_title('Sentiment Distribution', fontsize=13, fontweight='bold', pad=10)

    # Platform Comparison
    ax_platform = fig.add_subplot(gs[1, 3])

    platforms = ['iOS App Store', 'Google Play']
    ios_rating = data['summary']['ios_average_rating']
    gplay_rating = data['summary']['gplay_average_rating']
    ratings_platform = [ios_rating, gplay_rating]

    bars = ax_platform.bar(platforms, ratings_platform, color=[hp_blue, '#3ddc84'],
                           edgecolor='white', width=0.5)

    for bar, rating in zip(bars, ratings_platform):
        ax_platform.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{rating:.2f}', ha='center', fontsize=14, fontweight='bold')

    ax_platform.set_ylabel('Average Rating', fontsize=11)
    ax_platform.set_ylim(0, 5)
    ax_platform.axhline(y=3, color='#e74c3c', linestyle='--', alpha=0.5, label='Target: 3.0')
    ax_platform.set_title('Platform Comparison', fontsize=13, fontweight='bold', pad=10)
    ax_platform.spines['top'].set_visible(False)
    ax_platform.spines['right'].set_visible(False)

    # =========================================================================
    # ROW 3: Top Issues
    # =========================================================================

    ax_issues = fig.add_subplot(gs[2, :])

    top_issues = data['top_issues'][:8]
    issue_names = [issue['name'][:25] + '...' if len(issue['name']) > 25 else issue['name']
                   for issue in top_issues]
    issue_counts = [issue['mention_count'] for issue in top_issues]
    issue_pcts = [issue['percentage'] for issue in top_issues]

    # Calculate negative percentage for each issue
    neg_pcts = []
    for issue in top_issues:
        sent = issue['sentiment']
        total_sent = sent.get('positive', 0) + sent.get('negative', 0) + sent.get('neutral', 0)
        neg_pct = sent.get('negative', 0) / total_sent * 100 if total_sent > 0 else 0
        neg_pcts.append(neg_pct)

    x = np.arange(len(issue_names))
    width = 0.35

    bars1 = ax_issues.bar(x - width/2, issue_pcts, width, label='% of Reviews',
                          color=hp_blue, edgecolor='white')
    bars2 = ax_issues.bar(x + width/2, neg_pcts, width, label='% Negative Sentiment',
                          color='#e74c3c', edgecolor='white')

    ax_issues.set_ylabel('Percentage', fontsize=11)
    ax_issues.set_title('Top Customer Issues - Mentions vs Negative Sentiment',
                        fontsize=13, fontweight='bold', pad=10)
    ax_issues.set_xticks(x)
    ax_issues.set_xticklabels(issue_names, rotation=25, ha='right', fontsize=10)
    ax_issues.legend(loc='upper right', fontsize=10)
    ax_issues.spines['top'].set_visible(False)
    ax_issues.spines['right'].set_visible(False)

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax_issues.text(bar.get_x() + bar.get_width()/2, height + 1,
                      f'{height:.0f}%', ha='center', fontsize=9, fontweight='bold', color=hp_blue)

    for bar in bars2:
        height = bar.get_height()
        ax_issues.text(bar.get_x() + bar.get_width()/2, height + 1,
                      f'{height:.0f}%', ha='center', fontsize=9, fontweight='bold', color='#e74c3c')

    # Footer
    fig.text(0.5, 0.01,
             f'Generated by CustomerInsight_Review_Agent v1.1 | Analysis Date: {datetime.now().strftime("%Y-%m-%d")} | Data: US Market Only',
             ha='center', fontsize=9, color='#777')

    plt.savefig('HP_App_US_Executive_Dashboard.png', dpi=150, bbox_inches='tight',
                facecolor='#f8f9fa', edgecolor='none')
    print("✅ Saved: HP_App_US_Executive_Dashboard.png")
    plt.close()


# ============================================================================
# 2. iOS APP STORE ANALYSIS
# ============================================================================

def create_ios_analysis():
    """Create separate iOS App Store analysis visualization"""

    # Load iOS reviews
    with open("HP_App_US_Oct_iOS_Reviews.json", "r") as f:
        ios_reviews = json.load(f)

    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('#f0f4f8')

    fig.suptitle('HP Smart App - iOS App Store Analysis\nUS Market | October 2025 - January 2026',
                 fontsize=16, fontweight='bold', y=0.98, color='#333')

    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3,
                  left=0.08, right=0.95, top=0.90, bottom=0.08)

    # Colors - Apple style
    apple_blue = '#007AFF'
    apple_gray = '#8E8E93'

    # Calculate metrics
    total = len(ios_reviews)
    ratings = [r.get('rating', 0) for r in ios_reviews]
    avg_rating = sum(ratings) / total if total > 0 else 0
    rating_dist = {}
    for r in ratings:
        rating_dist[r] = rating_dist.get(r, 0) + 1

    # =========================================================================
    # Key Metrics Panel
    # =========================================================================

    ax_metrics = fig.add_subplot(gs[0, :])
    ax_metrics.axis('off')

    one_star = rating_dist.get(1, 0)
    five_star = rating_dist.get(5, 0)
    one_star_pct = one_star / total * 100
    five_star_pct = five_star / total * 100

    metrics_text = [
        (f"{total}", "Total Reviews", apple_blue),
        (f"{avg_rating:.2f}", "Avg Rating", '#FF3B30'),
        (f"{one_star_pct:.1f}%", "1-Star", '#FF3B30'),
        (f"{five_star_pct:.1f}%", "5-Star", '#34C759'),
    ]

    for i, (value, label, color) in enumerate(metrics_text):
        x = 0.12 + i * 0.22

        rect = mpatches.FancyBboxPatch((x, 0.2), 0.18, 0.6,
                                        boxstyle="round,pad=0.02",
                                        facecolor='white', edgecolor=color,
                                        linewidth=2, transform=ax_metrics.transAxes)
        ax_metrics.add_patch(rect)

        ax_metrics.text(x + 0.09, 0.55, value, fontsize=24, fontweight='bold',
                       ha='center', va='center', color=color, transform=ax_metrics.transAxes)
        ax_metrics.text(x + 0.09, 0.3, label, fontsize=11,
                       ha='center', va='center', color='#555', transform=ax_metrics.transAxes)

    # Apple logo indicator
    ax_metrics.text(0.02, 0.5, '🍎', fontsize=30, transform=ax_metrics.transAxes, va='center')

    # =========================================================================
    # Rating Distribution
    # =========================================================================

    ax_rating = fig.add_subplot(gs[1, 0:2])

    stars = ['5★', '4★', '3★', '2★', '1★']
    counts = [rating_dist.get(5-i, 0) for i in range(5)]
    percentages = [c/total*100 for c in counts]
    colors = ['#34C759', '#30D158', '#FFD60A', '#FF9F0A', '#FF3B30']

    bars = ax_rating.barh(stars, percentages, color=colors, edgecolor='white', height=0.6)

    for bar, pct, count in zip(bars, percentages, counts):
        ax_rating.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                      f'{pct:.1f}% ({count})', va='center', fontsize=10, fontweight='bold')

    ax_rating.set_xlabel('Percentage', fontsize=11)
    ax_rating.set_title('iOS Rating Distribution', fontsize=13, fontweight='bold')
    ax_rating.set_xlim(0, 70)
    ax_rating.spines['top'].set_visible(False)
    ax_rating.spines['right'].set_visible(False)

    # =========================================================================
    # Top Issues (iOS specific)
    # =========================================================================

    ax_issues = fig.add_subplot(gs[1, 2])

    ios_top = data['ios_analysis']['top_categories'][:5]

    # Category name mapping
    cat_names = {
        'printing': 'Print Quality',
        'mobile_experience': 'App Experience',
        'value': 'Value/Pricing',
        'features': 'Features',
        'connectivity': 'Connectivity',
        'reliability': 'Reliability',
        'scanning': 'Scanning',
        'updates': 'Updates',
        'account_cloud': 'Account',
        'support': 'Support',
        'uncategorized': 'Other'
    }

    issue_names = [cat_names.get(cat, cat)[:12] for cat, _ in ios_top]
    issue_counts = [count for _, count in ios_top]

    bars = ax_issues.barh(issue_names[::-1], issue_counts[::-1], color=apple_blue,
                          edgecolor='white', height=0.6)

    for bar in bars:
        ax_issues.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                      f'{int(bar.get_width())}', va='center', fontsize=10, fontweight='bold')

    ax_issues.set_xlabel('Mentions', fontsize=11)
    ax_issues.set_title('Top 5 iOS Issues', fontsize=13, fontweight='bold')
    ax_issues.spines['top'].set_visible(False)
    ax_issues.spines['right'].set_visible(False)

    # =========================================================================
    # Version Distribution
    # =========================================================================

    ax_version = fig.add_subplot(gs[2, 0])

    versions = {}
    for r in ios_reviews:
        v = r.get('version', 'Unknown')
        if v:
            versions[v] = versions.get(v, 0) + 1

    top_versions = sorted(versions.items(), key=lambda x: -x[1])[:5]
    v_names = [v[:10] for v, _ in top_versions]
    v_counts = [c for _, c in top_versions]

    ax_version.pie(v_counts, labels=v_names, autopct='%1.0f%%',
                   colors=['#007AFF', '#5856D6', '#AF52DE', '#FF2D55', '#FF9500'],
                   startangle=90, textprops={'fontsize': 9})
    ax_version.set_title('Top App Versions', fontsize=12, fontweight='bold')

    # =========================================================================
    # Sentiment Distribution
    # =========================================================================

    ax_sent = fig.add_subplot(gs[2, 1])

    ios_sent = data['ios_analysis']['sentiment']
    total_sent = sum(ios_sent.values())

    sent_labels = ['Positive', 'Negative', 'Neutral']
    sent_values = [ios_sent.get('positive', 0), ios_sent.get('negative', 0), ios_sent.get('neutral', 0)]
    sent_pcts = [v/total_sent*100 for v in sent_values]
    sent_colors = ['#34C759', '#FF3B30', '#8E8E93']

    bars = ax_sent.bar(sent_labels, sent_pcts, color=sent_colors, edgecolor='white', width=0.6)

    for bar, pct in zip(bars, sent_pcts):
        ax_sent.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{pct:.1f}%', ha='center', fontsize=11, fontweight='bold')

    ax_sent.set_ylabel('Percentage', fontsize=11)
    ax_sent.set_title('iOS Sentiment', fontsize=12, fontweight='bold')
    ax_sent.set_ylim(0, 50)
    ax_sent.spines['top'].set_visible(False)
    ax_sent.spines['right'].set_visible(False)

    # =========================================================================
    # Key Insights Box
    # =========================================================================

    ax_insights = fig.add_subplot(gs[2, 2])
    ax_insights.axis('off')

    insights_text = f"""
iOS App Store Key Insights

📊 Average Rating: {avg_rating:.2f}/5.0

🔴 Critical: {one_star_pct:.0f}% are 1-star reviews

📱 Top Issue: Print Quality
   ({ios_top[0][1]} mentions)

⚠️ Negative Sentiment:
   {ios_sent.get('negative', 0)/total_sent*100:.1f}%

✅ Positive Sentiment:
   {ios_sent.get('positive', 0)/total_sent*100:.1f}%
"""

    ax_insights.text(0.1, 0.95, insights_text, transform=ax_insights.transAxes,
                    fontsize=11, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='white', edgecolor=apple_blue, linewidth=2))

    # Footer
    fig.text(0.5, 0.02,
             f'iOS App Store Analysis | Generated: {datetime.now().strftime("%Y-%m-%d")} | CustomerInsight_Review_Agent v1.1',
             ha='center', fontsize=9, color='#777')

    plt.savefig('HP_App_US_iOS_Analysis.png', dpi=150, bbox_inches='tight',
                facecolor='#f0f4f8', edgecolor='none')
    print("✅ Saved: HP_App_US_iOS_Analysis.png")
    plt.close()


# ============================================================================
# 3. GOOGLE PLAY ANALYSIS
# ============================================================================

def create_android_analysis():
    """Create separate Google Play Store analysis visualization"""

    # Load Android reviews
    with open("HP_App_US_Oct_GooglePlay_Reviews.json", "r") as f:
        android_reviews = json.load(f)

    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('#e8f5e9')

    fig.suptitle('HP Smart App - Google Play Store Analysis\nUS Market | October 2025 - January 2026',
                 fontsize=16, fontweight='bold', y=0.98, color='#333')

    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3,
                  left=0.08, right=0.95, top=0.90, bottom=0.08)

    # Colors - Google/Material style
    google_green = '#3DDC84'
    google_blue = '#4285F4'
    google_red = '#EA4335'
    google_yellow = '#FBBC05'

    # Calculate metrics
    total = len(android_reviews)
    ratings = [r.get('rating', 0) for r in android_reviews]
    avg_rating = sum(ratings) / total if total > 0 else 0
    rating_dist = {}
    for r in ratings:
        rating_dist[r] = rating_dist.get(r, 0) + 1

    # =========================================================================
    # Key Metrics Panel
    # =========================================================================

    ax_metrics = fig.add_subplot(gs[0, :])
    ax_metrics.axis('off')

    one_star = rating_dist.get(1, 0)
    five_star = rating_dist.get(5, 0)
    one_star_pct = one_star / total * 100
    five_star_pct = five_star / total * 100

    metrics_text = [
        (f"{total}", "Total Reviews", google_green),
        (f"{avg_rating:.2f}", "Avg Rating", google_red),
        (f"{one_star_pct:.1f}%", "1-Star", google_red),
        (f"{five_star_pct:.1f}%", "5-Star", google_green),
    ]

    for i, (value, label, color) in enumerate(metrics_text):
        x = 0.12 + i * 0.22

        rect = mpatches.FancyBboxPatch((x, 0.2), 0.18, 0.6,
                                        boxstyle="round,pad=0.02",
                                        facecolor='white', edgecolor=color,
                                        linewidth=2, transform=ax_metrics.transAxes)
        ax_metrics.add_patch(rect)

        ax_metrics.text(x + 0.09, 0.55, value, fontsize=24, fontweight='bold',
                       ha='center', va='center', color=color, transform=ax_metrics.transAxes)
        ax_metrics.text(x + 0.09, 0.3, label, fontsize=11,
                       ha='center', va='center', color='#555', transform=ax_metrics.transAxes)

    # Android indicator
    ax_metrics.text(0.02, 0.5, '🤖', fontsize=30, transform=ax_metrics.transAxes, va='center')

    # =========================================================================
    # Rating Distribution
    # =========================================================================

    ax_rating = fig.add_subplot(gs[1, 0:2])

    stars = ['5★', '4★', '3★', '2★', '1★']
    counts = [rating_dist.get(5-i, 0) for i in range(5)]
    percentages = [c/total*100 for c in counts]
    colors = [google_green, '#66BB6A', google_yellow, '#FF9800', google_red]

    bars = ax_rating.barh(stars, percentages, color=colors, edgecolor='white', height=0.6)

    for bar, pct, count in zip(bars, percentages, counts):
        ax_rating.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                      f'{pct:.1f}% ({count})', va='center', fontsize=10, fontweight='bold')

    ax_rating.set_xlabel('Percentage', fontsize=11)
    ax_rating.set_title('Google Play Rating Distribution', fontsize=13, fontweight='bold')
    ax_rating.set_xlim(0, 75)
    ax_rating.spines['top'].set_visible(False)
    ax_rating.spines['right'].set_visible(False)

    # =========================================================================
    # Top Issues (Android specific)
    # =========================================================================

    ax_issues = fig.add_subplot(gs[1, 2])

    gplay_top = data['gplay_analysis']['top_categories'][:5]

    cat_names = {
        'printing': 'Print Quality',
        'mobile_experience': 'App Experience',
        'value': 'Value/Pricing',
        'features': 'Features',
        'connectivity': 'Connectivity',
        'reliability': 'Reliability',
        'scanning': 'Scanning',
        'updates': 'Updates',
        'account_cloud': 'Account',
        'support': 'Support',
        'uncategorized': 'Other'
    }

    issue_names = [cat_names.get(cat, cat)[:12] for cat, _ in gplay_top]
    issue_counts = [count for _, count in gplay_top]

    bars = ax_issues.barh(issue_names[::-1], issue_counts[::-1], color=google_green,
                          edgecolor='white', height=0.6)

    for bar in bars:
        ax_issues.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                      f'{int(bar.get_width())}', va='center', fontsize=10, fontweight='bold')

    ax_issues.set_xlabel('Mentions', fontsize=11)
    ax_issues.set_title('Top 5 Android Issues', fontsize=13, fontweight='bold')
    ax_issues.spines['top'].set_visible(False)
    ax_issues.spines['right'].set_visible(False)

    # =========================================================================
    # Version Distribution
    # =========================================================================

    ax_version = fig.add_subplot(gs[2, 0])

    versions = {}
    for r in android_reviews:
        v = r.get('version', 'Unknown')
        if v:
            versions[v] = versions.get(v, 0) + 1

    top_versions = sorted(versions.items(), key=lambda x: -x[1])[:5]
    v_names = [v[:12] for v, _ in top_versions]
    v_counts = [c for _, c in top_versions]

    ax_version.pie(v_counts, labels=v_names, autopct='%1.0f%%',
                   colors=[google_green, google_blue, google_yellow, google_red, '#9E9E9E'],
                   startangle=90, textprops={'fontsize': 9})
    ax_version.set_title('Top App Versions', fontsize=12, fontweight='bold')

    # =========================================================================
    # Sentiment Distribution
    # =========================================================================

    ax_sent = fig.add_subplot(gs[2, 1])

    gplay_sent = data['gplay_analysis']['sentiment']
    total_sent = sum(gplay_sent.values())

    sent_labels = ['Positive', 'Negative', 'Neutral']
    sent_values = [gplay_sent.get('positive', 0), gplay_sent.get('negative', 0), gplay_sent.get('neutral', 0)]
    sent_pcts = [v/total_sent*100 for v in sent_values]
    sent_colors = [google_green, google_red, '#9E9E9E']

    bars = ax_sent.bar(sent_labels, sent_pcts, color=sent_colors, edgecolor='white', width=0.6)

    for bar, pct in zip(bars, sent_pcts):
        ax_sent.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{pct:.1f}%', ha='center', fontsize=11, fontweight='bold')

    ax_sent.set_ylabel('Percentage', fontsize=11)
    ax_sent.set_title('Android Sentiment', fontsize=12, fontweight='bold')
    ax_sent.set_ylim(0, 55)
    ax_sent.spines['top'].set_visible(False)
    ax_sent.spines['right'].set_visible(False)

    # =========================================================================
    # Key Insights Box
    # =========================================================================

    ax_insights = fig.add_subplot(gs[2, 2])
    ax_insights.axis('off')

    insights_text = f"""
Google Play Key Insights

📊 Average Rating: {avg_rating:.2f}/5.0

🔴 Critical: {one_star_pct:.0f}% are 1-star reviews

📱 Top Issue: Print Quality
   ({gplay_top[0][1]} mentions)

⚠️ Negative Sentiment:
   {gplay_sent.get('negative', 0)/total_sent*100:.1f}%

✅ Positive Sentiment:
   {gplay_sent.get('positive', 0)/total_sent*100:.1f}%
"""

    ax_insights.text(0.1, 0.95, insights_text, transform=ax_insights.transAxes,
                    fontsize=11, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='white', edgecolor=google_green, linewidth=2))

    # Footer
    fig.text(0.5, 0.02,
             f'Google Play Analysis | Generated: {datetime.now().strftime("%Y-%m-%d")} | CustomerInsight_Review_Agent v1.1',
             ha='center', fontsize=9, color='#777')

    plt.savefig('HP_App_US_Android_Analysis.png', dpi=150, bbox_inches='tight',
                facecolor='#e8f5e9', edgecolor='none')
    print("✅ Saved: HP_App_US_Android_Analysis.png")
    plt.close()


# ============================================================================
# 4. PLATFORM COMPARISON CHART
# ============================================================================

def create_platform_comparison():
    """Create side-by-side platform comparison"""

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('white')
    fig.suptitle('HP Smart App - iOS vs Android Comparison\nUS Market | October 2025+',
                 fontsize=14, fontweight='bold', y=1.02)

    # Colors
    ios_color = '#007AFF'
    android_color = '#3DDC84'

    # 1. Rating Comparison
    ax1 = axes[0]
    platforms = ['iOS App Store', 'Google Play']
    ratings = [data['summary']['ios_average_rating'], data['summary']['gplay_average_rating']]

    bars = ax1.bar(platforms, ratings, color=[ios_color, android_color], width=0.5, edgecolor='white')

    for bar, rating in zip(bars, ratings):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{rating:.2f}', ha='center', fontsize=14, fontweight='bold')

    ax1.set_ylim(0, 5)
    ax1.axhline(y=3, color='#e74c3c', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Average Rating', fontsize=11)
    ax1.set_title('Average Rating Comparison', fontsize=12, fontweight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # 2. Sentiment Comparison
    ax2 = axes[1]

    ios_sent = data['ios_analysis']['sentiment']
    gplay_sent = data['gplay_analysis']['sentiment']

    ios_total = sum(ios_sent.values())
    gplay_total = sum(gplay_sent.values())

    x = np.arange(3)
    width = 0.35

    ios_pcts = [ios_sent.get(s, 0)/ios_total*100 for s in ['positive', 'negative', 'neutral']]
    gplay_pcts = [gplay_sent.get(s, 0)/gplay_total*100 for s in ['positive', 'negative', 'neutral']]

    bars1 = ax2.bar(x - width/2, ios_pcts, width, label='iOS', color=ios_color)
    bars2 = ax2.bar(x + width/2, gplay_pcts, width, label='Android', color=android_color)

    ax2.set_ylabel('Percentage', fontsize=11)
    ax2.set_title('Sentiment Comparison', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Positive', 'Negative', 'Neutral'])
    ax2.legend()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # 3. Top Issues Comparison
    ax3 = axes[2]

    cat_names = {
        'printing': 'Print Quality',
        'mobile_experience': 'App Experience',
        'value': 'Value/Pricing',
        'features': 'Features',
        'connectivity': 'Connectivity',
        'uncategorized': 'Other'
    }

    ios_top = dict(data['ios_analysis']['top_categories'][:5])
    gplay_top = dict(data['gplay_analysis']['top_categories'][:5])

    all_cats = list(set(ios_top.keys()) | set(gplay_top.keys()))[:5]

    x = np.arange(len(all_cats))
    width = 0.35

    ios_counts = [ios_top.get(cat, 0) for cat in all_cats]
    gplay_counts = [gplay_top.get(cat, 0) for cat in all_cats]
    cat_labels = [cat_names.get(cat, cat)[:10] for cat in all_cats]

    bars1 = ax3.bar(x - width/2, ios_counts, width, label='iOS', color=ios_color)
    bars2 = ax3.bar(x + width/2, gplay_counts, width, label='Android', color=android_color)

    ax3.set_ylabel('Mentions', fontsize=11)
    ax3.set_title('Top Issues by Platform', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(cat_labels, rotation=20, ha='right')
    ax3.legend()
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('HP_App_US_Platform_Comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✅ Saved: HP_App_US_Platform_Comparison.png")
    plt.close()


# ============================================================================
# RUN ALL VISUALIZATIONS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CREATING HP APP US MARKET VISUALIZATIONS")
    print("="*60 + "\n")

    print("1. Creating Executive Dashboard...")
    create_executive_dashboard()

    print("\n2. Creating iOS App Store Analysis...")
    create_ios_analysis()

    print("\n3. Creating Google Play Analysis...")
    create_android_analysis()

    print("\n4. Creating Platform Comparison...")
    create_platform_comparison()

    print("\n" + "="*60)
    print("ALL VISUALIZATIONS COMPLETE")
    print("="*60)
    print("""
Files Generated:
  1. HP_App_US_Executive_Dashboard.png  - Combined executive view
  2. HP_App_US_iOS_Analysis.png         - iOS App Store detailed analysis
  3. HP_App_US_Android_Analysis.png     - Google Play detailed analysis
  4. HP_App_US_Platform_Comparison.png  - Side-by-side comparison
""")
