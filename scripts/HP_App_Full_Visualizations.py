"""
================================================================================
HP App - Full Visualizations with Date Information
iOS App Store + Google Play Store - US Market
October 2025 - January 2026
================================================================================
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from datetime import datetime
from collections import Counter

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.titleweight'] = 'bold'

# Load data
with open("HP_App_US_Full_Insights_Oct2025.json", "r") as f:
    data = json.load(f)

with open("HP_App_iOS_US_Oct2025_Full.json", "r") as f:
    ios_reviews = json.load(f)

with open("HP_App_GooglePlay_US_Oct2025_Full.json", "r") as f:
    gplay_reviews = json.load(f)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_date_range(reviews, date_key='date'):
    """Get date range from reviews"""
    dates = []
    for r in reviews:
        date_str = r.get(date_key, '')
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.split('+')[0].split('-07:00')[0].replace('Z', ''))
                dates.append(dt)
            except:
                pass
    if dates:
        return min(dates), max(dates), len(dates)
    return None, None, 0

# ============================================================================
# 1. EXECUTIVE DASHBOARD WITH DATES
# ============================================================================

def create_executive_dashboard():
    """Create executive dashboard with date information"""

    fig = plt.figure(figsize=(20, 16))
    fig.patch.set_facecolor('#f8f9fa')

    # Get date ranges
    ios_earliest, ios_latest, ios_count = get_date_range(ios_reviews)
    gplay_earliest, gplay_latest, gplay_count = get_date_range(gplay_reviews)

    ios_days = (ios_latest - ios_earliest).days if ios_earliest and ios_latest else 0
    gplay_days = (gplay_latest - gplay_earliest).days if gplay_earliest and gplay_latest else 0

    # Title with date info
    fig.suptitle('HP Smart App - US Market Executive Dashboard\nOctober 2025 - January 2026 | Full Data Analysis',
                 fontsize=18, fontweight='bold', y=0.98, color='#2c3e50')

    gs = GridSpec(4, 4, figure=fig, hspace=0.4, wspace=0.3,
                  left=0.05, right=0.95, top=0.92, bottom=0.05)

    # Colors
    hp_blue = '#0096D6'
    ios_color = '#007AFF'
    android_color = '#3DDC84'

    # =========================================================================
    # ROW 0: Date Information Banner
    # =========================================================================

    ax_dates = fig.add_subplot(gs[0, :])
    ax_dates.axis('off')
    ax_dates.set_xlim(0, 1)
    ax_dates.set_ylim(0, 1)

    # Date info boxes
    date_info = [
        ("iOS App Store", f"{ios_count:,} reviews",
         f"{ios_earliest.strftime('%b %d') if ios_earliest else 'N/A'} - {ios_latest.strftime('%b %d, %Y') if ios_latest else 'N/A'}",
         f"{ios_days} days", ios_color),
        ("Google Play", f"{gplay_count:,} reviews",
         f"{gplay_earliest.strftime('%b %d') if gplay_earliest else 'N/A'} - {gplay_latest.strftime('%b %d, %Y') if gplay_latest else 'N/A'}",
         f"{gplay_days} days", android_color),
        ("Combined Total", f"{ios_count + gplay_count:,} reviews",
         f"{gplay_earliest.strftime('%b %d, %Y') if gplay_earliest else 'N/A'} - {gplay_latest.strftime('%b %d, %Y') if gplay_latest else 'N/A'}",
         "Full Period", hp_blue),
    ]

    for i, (platform, reviews, date_range, days, color) in enumerate(date_info):
        x = 0.05 + i * 0.32

        # Box
        rect = mpatches.FancyBboxPatch((x, 0.1), 0.28, 0.8,
                                        boxstyle="round,pad=0.02",
                                        facecolor='white', edgecolor=color,
                                        linewidth=3, transform=ax_dates.transAxes)
        ax_dates.add_patch(rect)

        # Platform name
        ax_dates.text(x + 0.14, 0.75, platform, fontsize=14, fontweight='bold',
                     ha='center', va='center', color=color, transform=ax_dates.transAxes)
        # Reviews count
        ax_dates.text(x + 0.14, 0.55, reviews, fontsize=18, fontweight='bold',
                     ha='center', va='center', color='#333', transform=ax_dates.transAxes)
        # Date range
        ax_dates.text(x + 0.14, 0.35, date_range, fontsize=10,
                     ha='center', va='center', color='#555', transform=ax_dates.transAxes)
        # Days span
        ax_dates.text(x + 0.14, 0.2, f"({days})", fontsize=10,
                     ha='center', va='center', color='#777', transform=ax_dates.transAxes)

    # =========================================================================
    # ROW 1: Key Metrics
    # =========================================================================

    ax_metrics = fig.add_subplot(gs[1, :])
    ax_metrics.axis('off')
    ax_metrics.set_xlim(0, 1)
    ax_metrics.set_ylim(0, 1)

    total = data['summary']['total_reviews']

    metrics = [
        (f"{total:,}", "Total Reviews", hp_blue),
        (f"{data['summary']['combined_avg_rating']:.2f}/5.0", "Avg Rating", '#e74c3c'),
        (f"{data['rating_distribution'].get('1', 0)/total*100:.0f}%", "1-Star Reviews", '#c0392b'),
        (f"{data['sentiment']['negative']/total*100:.0f}%", "Negative Sentiment", '#e74c3c'),
        (f"{data['summary']['ios_avg_rating']:.2f}", "iOS Rating", ios_color),
        (f"{data['summary']['gplay_avg_rating']:.2f}", "Android Rating", android_color),
    ]

    box_width = 0.14
    start_x = 0.04

    for i, (value, label, color) in enumerate(metrics):
        x = start_x + i * 0.16

        rect = mpatches.FancyBboxPatch((x, 0.15), box_width, 0.7,
                                        boxstyle="round,pad=0.02",
                                        facecolor='white', edgecolor=color,
                                        linewidth=2, transform=ax_metrics.transAxes)
        ax_metrics.add_patch(rect)

        ax_metrics.text(x + box_width/2, 0.55, value, fontsize=20, fontweight='bold',
                       ha='center', va='center', color=color, transform=ax_metrics.transAxes)
        ax_metrics.text(x + box_width/2, 0.28, label, fontsize=9, fontweight='bold',
                       ha='center', va='center', color='#333', transform=ax_metrics.transAxes)

    # =========================================================================
    # ROW 2: Rating Distribution + Platform Comparison
    # =========================================================================

    # Rating Distribution
    ax_rating = fig.add_subplot(gs[2, 0:2])

    rating_dist = data['rating_distribution']
    stars = ['5 Star', '4 Star', '3 Star', '2 Star', '1 Star']
    counts = [rating_dist.get(str(5-i), 0) for i in range(5)]
    percentages = [c/total*100 for c in counts]
    colors_rating = ['#27ae60', '#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']

    bars = ax_rating.barh(stars, percentages, color=colors_rating, edgecolor='white', height=0.6)

    for bar, pct, count in zip(bars, percentages, counts):
        ax_rating.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                      f'{pct:.1f}% ({count:,})', va='center', fontsize=10, fontweight='bold')

    ax_rating.set_xlabel('Percentage of Reviews', fontsize=11)
    ax_rating.set_title(f'Rating Distribution (n={total:,})', fontsize=13, fontweight='bold')
    ax_rating.set_xlim(0, 80)
    ax_rating.spines['top'].set_visible(False)
    ax_rating.spines['right'].set_visible(False)

    # Platform Rating Comparison
    ax_platform = fig.add_subplot(gs[2, 2:4])

    # Data for grouped bar chart
    categories = ['Avg Rating', '1-Star %', '5-Star %', 'Negative %']

    ios_data = data['ios_analysis']
    gplay_data = data['gplay_analysis']

    ios_1star = ios_data['rating_distribution'].get(1, 0) / ios_data['total'] * 100
    ios_5star = ios_data['rating_distribution'].get(5, 0) / ios_data['total'] * 100
    ios_neg = ios_data['sentiment'].get('negative', 0) / ios_data['total'] * 100

    gplay_1star = gplay_data['rating_distribution'].get(1, 0) / gplay_data['total'] * 100
    gplay_5star = gplay_data['rating_distribution'].get(5, 0) / gplay_data['total'] * 100
    gplay_neg = gplay_data['sentiment'].get('negative', 0) / gplay_data['total'] * 100

    x = np.arange(4)
    width = 0.35

    ios_vals = [data['summary']['ios_avg_rating']*20, ios_1star, ios_5star, ios_neg]
    gplay_vals = [data['summary']['gplay_avg_rating']*20, gplay_1star, gplay_5star, gplay_neg]

    bars1 = ax_platform.bar(x - width/2, ios_vals, width, label=f'iOS ({ios_days} days)', color=ios_color)
    bars2 = ax_platform.bar(x + width/2, gplay_vals, width, label=f'Android ({gplay_days} days)', color=android_color)

    # Add value labels
    labels_ios = [f'{data["summary"]["ios_avg_rating"]:.2f}', f'{ios_1star:.0f}%', f'{ios_5star:.0f}%', f'{ios_neg:.0f}%']
    labels_gplay = [f'{data["summary"]["gplay_avg_rating"]:.2f}', f'{gplay_1star:.0f}%', f'{gplay_5star:.0f}%', f'{gplay_neg:.0f}%']

    for bar, label in zip(bars1, labels_ios):
        ax_platform.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        label, ha='center', fontsize=9, fontweight='bold', color=ios_color)

    for bar, label in zip(bars2, labels_gplay):
        ax_platform.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        label, ha='center', fontsize=9, fontweight='bold', color=android_color)

    ax_platform.set_ylabel('Value / Percentage', fontsize=11)
    ax_platform.set_title('iOS vs Android Comparison', fontsize=13, fontweight='bold')
    ax_platform.set_xticks(x)
    ax_platform.set_xticklabels(['Avg Rating\n(x20 scale)', '1-Star %', '5-Star %', 'Negative %'])
    ax_platform.legend(loc='upper right')
    ax_platform.spines['top'].set_visible(False)
    ax_platform.spines['right'].set_visible(False)

    # =========================================================================
    # ROW 3: Top Issues
    # =========================================================================

    ax_issues = fig.add_subplot(gs[3, :])

    top_issues = data['top_issues'][:8]
    issue_names = [issue['name'][:20] + '...' if len(issue['name']) > 20 else issue['name']
                   for issue in top_issues]
    issue_pcts = [issue['percentage'] for issue in top_issues]

    neg_pcts = []
    for issue in top_issues:
        sent = issue['sentiment']
        total_sent = sent.get('positive', 0) + sent.get('negative', 0) + sent.get('neutral', 0)
        neg_pct = sent.get('negative', 0) / total_sent * 100 if total_sent > 0 else 0
        neg_pcts.append(neg_pct)

    x = np.arange(len(issue_names))
    width = 0.35

    bars1 = ax_issues.bar(x - width/2, issue_pcts, width, label='% of Reviews', color=hp_blue)
    bars2 = ax_issues.bar(x + width/2, neg_pcts, width, label='% Negative Sentiment', color='#e74c3c')

    ax_issues.set_ylabel('Percentage', fontsize=11)
    ax_issues.set_title('Top Customer Issues - Mentions vs Negative Sentiment', fontsize=13, fontweight='bold')
    ax_issues.set_xticks(x)
    ax_issues.set_xticklabels(issue_names, rotation=25, ha='right', fontsize=10)
    ax_issues.legend(loc='upper right')
    ax_issues.spines['top'].set_visible(False)
    ax_issues.spines['right'].set_visible(False)

    for bar in bars1:
        ax_issues.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                      f'{bar.get_height():.0f}%', ha='center', fontsize=8, color=hp_blue)

    for bar in bars2:
        ax_issues.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                      f'{bar.get_height():.0f}%', ha='center', fontsize=8, color='#e74c3c')

    # Footer
    fig.text(0.5, 0.01,
             f'Generated by CustomerInsight_Review_Agent v1.1 | Analysis Date: {datetime.now().strftime("%Y-%m-%d")} | Data: {total:,} US Reviews',
             ha='center', fontsize=9, color='#777')

    plt.savefig('HP_App_Full_Executive_Dashboard.png', dpi=150, bbox_inches='tight',
                facecolor='#f8f9fa', edgecolor='none')
    print("Saved: HP_App_Full_Executive_Dashboard.png")
    plt.close()


# ============================================================================
# 2. iOS ANALYSIS WITH DATES
# ============================================================================

def create_ios_analysis():
    """Create iOS analysis with date information"""

    ios_earliest, ios_latest, ios_count = get_date_range(ios_reviews)
    ios_days = (ios_latest - ios_earliest).days if ios_earliest and ios_latest else 0

    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('#f0f4f8')

    date_str = f"{ios_earliest.strftime('%b %d') if ios_earliest else 'N/A'} - {ios_latest.strftime('%b %d, %Y') if ios_latest else 'N/A'} ({ios_days} days)"

    fig.suptitle(f'HP Smart App - iOS App Store Analysis\nUS Market | {date_str} | {ios_count:,} Reviews',
                 fontsize=16, fontweight='bold', y=0.98, color='#333')

    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3,
                  left=0.08, right=0.95, top=0.88, bottom=0.08)

    ios_color = '#007AFF'

    # Calculate metrics
    ios_data = data['ios_analysis']
    total = ios_data['total']
    avg_rating = data['summary']['ios_avg_rating']
    rating_dist = ios_data['rating_distribution']

    one_star = rating_dist.get(1, 0)
    five_star = rating_dist.get(5, 0)
    one_star_pct = one_star / total * 100
    five_star_pct = five_star / total * 100

    # Key Metrics
    ax_metrics = fig.add_subplot(gs[0, :])
    ax_metrics.axis('off')

    metrics = [
        (f"{total:,}", "Total Reviews", ios_color),
        (f"{avg_rating:.2f}", "Avg Rating", '#FF3B30'),
        (f"{one_star_pct:.1f}%", "1-Star", '#FF3B30'),
        (f"{five_star_pct:.1f}%", "5-Star", '#34C759'),
        (f"{ios_days}", "Days of Data", '#8E8E93'),
    ]

    for i, (value, label, color) in enumerate(metrics):
        x = 0.08 + i * 0.18

        rect = mpatches.FancyBboxPatch((x, 0.2), 0.15, 0.6,
                                        boxstyle="round,pad=0.02",
                                        facecolor='white', edgecolor=color,
                                        linewidth=2, transform=ax_metrics.transAxes)
        ax_metrics.add_patch(rect)

        ax_metrics.text(x + 0.075, 0.55, value, fontsize=22, fontweight='bold',
                       ha='center', va='center', color=color, transform=ax_metrics.transAxes)
        ax_metrics.text(x + 0.075, 0.3, label, fontsize=10,
                       ha='center', va='center', color='#555', transform=ax_metrics.transAxes)

    # Rating Distribution
    ax_rating = fig.add_subplot(gs[1, 0:2])

    stars = ['5 Star', '4 Star', '3 Star', '2 Star', '1 Star']
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

    # Top Issues
    ax_issues = fig.add_subplot(gs[1, 2])

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

    ios_top = ios_data['top_categories'][:5]
    issue_names = [cat_names.get(cat, cat)[:12] for cat, _ in ios_top]
    issue_counts = [count for _, count in ios_top]

    bars = ax_issues.barh(issue_names[::-1], issue_counts[::-1], color=ios_color,
                          edgecolor='white', height=0.6)

    for bar in bars:
        ax_issues.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                      f'{int(bar.get_width())}', va='center', fontsize=10, fontweight='bold')

    ax_issues.set_xlabel('Mentions', fontsize=11)
    ax_issues.set_title('Top 5 iOS Issues', fontsize=13, fontweight='bold')
    ax_issues.spines['top'].set_visible(False)
    ax_issues.spines['right'].set_visible(False)

    # Sentiment
    ax_sent = fig.add_subplot(gs[2, 0])

    ios_sent = ios_data['sentiment']
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

    # Reviews by Week
    ax_weekly = fig.add_subplot(gs[2, 1:3])

    # Calculate weekly distribution
    weeks = Counter()
    for r in ios_reviews:
        date_str = r.get('date', '')
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.split('+')[0].split('-07:00')[0])
                week_start = dt - __import__('datetime').timedelta(days=dt.weekday())
                weeks[week_start.strftime('%m/%d')] += 1
            except:
                pass

    week_labels = list(sorted(weeks.keys()))
    week_counts = [weeks[w] for w in week_labels]

    ax_weekly.bar(week_labels, week_counts, color=ios_color, edgecolor='white')
    ax_weekly.set_xlabel('Week Starting', fontsize=11)
    ax_weekly.set_ylabel('Reviews', fontsize=11)
    ax_weekly.set_title('iOS Reviews by Week', fontsize=12, fontweight='bold')
    ax_weekly.tick_params(axis='x', rotation=45)
    ax_weekly.spines['top'].set_visible(False)
    ax_weekly.spines['right'].set_visible(False)

    for i, (w, c) in enumerate(zip(week_labels, week_counts)):
        ax_weekly.text(i, c + 2, str(c), ha='center', fontsize=9, fontweight='bold')

    # Footer
    fig.text(0.5, 0.02,
             f'iOS App Store Analysis | {date_str} | CustomerInsight_Review_Agent v1.1',
             ha='center', fontsize=9, color='#777')

    plt.savefig('HP_App_Full_iOS_Analysis.png', dpi=150, bbox_inches='tight',
                facecolor='#f0f4f8', edgecolor='none')
    print("Saved: HP_App_Full_iOS_Analysis.png")
    plt.close()


# ============================================================================
# 3. GOOGLE PLAY ANALYSIS WITH DATES
# ============================================================================

def create_android_analysis():
    """Create Google Play analysis with date information"""

    gplay_earliest, gplay_latest, gplay_count = get_date_range(gplay_reviews)
    gplay_days = (gplay_latest - gplay_earliest).days if gplay_earliest and gplay_latest else 0

    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('#e8f5e9')

    date_str = f"{gplay_earliest.strftime('%b %d') if gplay_earliest else 'N/A'} - {gplay_latest.strftime('%b %d, %Y') if gplay_latest else 'N/A'} ({gplay_days} days)"

    fig.suptitle(f'HP Smart App - Google Play Store Analysis\nUS Market | {date_str} | {gplay_count:,} Reviews',
                 fontsize=16, fontweight='bold', y=0.98, color='#333')

    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3,
                  left=0.08, right=0.95, top=0.88, bottom=0.08)

    android_color = '#3DDC84'
    google_red = '#EA4335'

    # Calculate metrics
    gplay_data = data['gplay_analysis']
    total = gplay_data['total']
    avg_rating = data['summary']['gplay_avg_rating']
    rating_dist = gplay_data['rating_distribution']

    one_star = rating_dist.get(1, 0)
    five_star = rating_dist.get(5, 0)
    one_star_pct = one_star / total * 100
    five_star_pct = five_star / total * 100

    # Key Metrics
    ax_metrics = fig.add_subplot(gs[0, :])
    ax_metrics.axis('off')

    metrics = [
        (f"{total:,}", "Total Reviews", android_color),
        (f"{avg_rating:.2f}", "Avg Rating", google_red),
        (f"{one_star_pct:.1f}%", "1-Star", google_red),
        (f"{five_star_pct:.1f}%", "5-Star", android_color),
        (f"{gplay_days}", "Days of Data", '#757575'),
    ]

    for i, (value, label, color) in enumerate(metrics):
        x = 0.08 + i * 0.18

        rect = mpatches.FancyBboxPatch((x, 0.2), 0.15, 0.6,
                                        boxstyle="round,pad=0.02",
                                        facecolor='white', edgecolor=color,
                                        linewidth=2, transform=ax_metrics.transAxes)
        ax_metrics.add_patch(rect)

        ax_metrics.text(x + 0.075, 0.55, value, fontsize=22, fontweight='bold',
                       ha='center', va='center', color=color, transform=ax_metrics.transAxes)
        ax_metrics.text(x + 0.075, 0.3, label, fontsize=10,
                       ha='center', va='center', color='#555', transform=ax_metrics.transAxes)

    # Rating Distribution
    ax_rating = fig.add_subplot(gs[1, 0:2])

    stars = ['5 Star', '4 Star', '3 Star', '2 Star', '1 Star']
    counts = [rating_dist.get(5-i, 0) for i in range(5)]
    percentages = [c/total*100 for c in counts]
    colors = [android_color, '#66BB6A', '#FBBC05', '#FF9800', google_red]

    bars = ax_rating.barh(stars, percentages, color=colors, edgecolor='white', height=0.6)

    for bar, pct, count in zip(bars, percentages, counts):
        ax_rating.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                      f'{pct:.1f}% ({count:,})', va='center', fontsize=10, fontweight='bold')

    ax_rating.set_xlabel('Percentage', fontsize=11)
    ax_rating.set_title('Google Play Rating Distribution', fontsize=13, fontweight='bold')
    ax_rating.set_xlim(0, 75)
    ax_rating.spines['top'].set_visible(False)
    ax_rating.spines['right'].set_visible(False)

    # Top Issues
    ax_issues = fig.add_subplot(gs[1, 2])

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

    gplay_top = gplay_data['top_categories'][:5]
    issue_names = [cat_names.get(cat, cat)[:12] for cat, _ in gplay_top]
    issue_counts = [count for _, count in gplay_top]

    bars = ax_issues.barh(issue_names[::-1], issue_counts[::-1], color=android_color,
                          edgecolor='white', height=0.6)

    for bar in bars:
        ax_issues.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                      f'{int(bar.get_width())}', va='center', fontsize=10, fontweight='bold')

    ax_issues.set_xlabel('Mentions', fontsize=11)
    ax_issues.set_title('Top 5 Android Issues', fontsize=13, fontweight='bold')
    ax_issues.spines['top'].set_visible(False)
    ax_issues.spines['right'].set_visible(False)

    # Sentiment
    ax_sent = fig.add_subplot(gs[2, 0])

    gplay_sent = gplay_data['sentiment']
    total_sent = sum(gplay_sent.values())

    sent_labels = ['Positive', 'Negative', 'Neutral']
    sent_values = [gplay_sent.get('positive', 0), gplay_sent.get('negative', 0), gplay_sent.get('neutral', 0)]
    sent_pcts = [v/total_sent*100 for v in sent_values]
    sent_colors = [android_color, google_red, '#9E9E9E']

    bars = ax_sent.bar(sent_labels, sent_pcts, color=sent_colors, edgecolor='white', width=0.6)

    for bar, pct in zip(bars, sent_pcts):
        ax_sent.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{pct:.1f}%', ha='center', fontsize=11, fontweight='bold')

    ax_sent.set_ylabel('Percentage', fontsize=11)
    ax_sent.set_title('Android Sentiment', fontsize=12, fontweight='bold')
    ax_sent.set_ylim(0, 55)
    ax_sent.spines['top'].set_visible(False)
    ax_sent.spines['right'].set_visible(False)

    # Reviews by Month
    ax_monthly = fig.add_subplot(gs[2, 1:3])

    months = Counter()
    for r in gplay_reviews:
        date_str = r.get('date', '')
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', ''))
                months[dt.strftime('%Y-%m')] += 1
            except:
                pass

    month_labels = list(sorted(months.keys()))
    month_names = []
    for m in month_labels:
        dt = datetime.strptime(m, '%Y-%m')
        month_names.append(dt.strftime('%b %Y'))
    month_counts = [months[m] for m in month_labels]

    bars = ax_monthly.bar(month_names, month_counts, color=android_color, edgecolor='white')
    ax_monthly.set_xlabel('Month', fontsize=11)
    ax_monthly.set_ylabel('Reviews', fontsize=11)
    ax_monthly.set_title('Google Play Reviews by Month', fontsize=12, fontweight='bold')
    ax_monthly.spines['top'].set_visible(False)
    ax_monthly.spines['right'].set_visible(False)

    for bar, c in zip(bars, month_counts):
        ax_monthly.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                       str(c), ha='center', fontsize=10, fontweight='bold')

    # Footer
    fig.text(0.5, 0.02,
             f'Google Play Analysis | {date_str} | CustomerInsight_Review_Agent v1.1',
             ha='center', fontsize=9, color='#777')

    plt.savefig('HP_App_Full_Android_Analysis.png', dpi=150, bbox_inches='tight',
                facecolor='#e8f5e9', edgecolor='none')
    print("Saved: HP_App_Full_Android_Analysis.png")
    plt.close()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CREATING HP APP VISUALIZATIONS WITH DATE INFORMATION")
    print("="*60 + "\n")

    print("1. Creating Executive Dashboard...")
    create_executive_dashboard()

    print("2. Creating iOS Analysis...")
    create_ios_analysis()

    print("3. Creating Android Analysis...")
    create_android_analysis()

    print("\n" + "="*60)
    print("ALL VISUALIZATIONS COMPLETE")
    print("="*60)
    print("""
Files Generated:
  1. HP_App_Full_Executive_Dashboard.png  - Executive view with dates
  2. HP_App_Full_iOS_Analysis.png         - iOS detailed analysis with dates
  3. HP_App_Full_Android_Analysis.png     - Android detailed analysis with dates
""")
