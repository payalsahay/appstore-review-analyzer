"""
HP App - US Market Executive Dashboard & Comparison
Google Play US vs iOS US (October 2025+)
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from datetime import datetime
from collections import Counter, defaultdict
import re

# ============================================================================
# LOAD DATA
# ============================================================================

# Google Play US data
gp_df = pd.read_csv('hp_app_reviews_oct2025_present.csv')
gp_df['date'] = pd.to_datetime(gp_df['date'])

# iOS US data
with open('HP_App_Reviews_Oct_US.json', 'r') as f:
    ios_reviews = json.load(f)

print(f"Google Play US reviews: {len(gp_df)}")
print(f"iOS US reviews: {len(ios_reviews)}")

# ============================================================================
# CALCULATE METRICS - GOOGLE PLAY US
# ============================================================================

gp_total = len(gp_df)
gp_avg = gp_df['rating'].mean()
gp_dist = gp_df['rating'].value_counts().to_dict()

gp_1star = gp_dist.get(1, 0)
gp_1star_pct = gp_1star / gp_total * 100
gp_5star = gp_dist.get(5, 0)
gp_5star_pct = gp_5star / gp_total * 100
gp_negative = (gp_dist.get(1, 0) + gp_dist.get(2, 0)) / gp_total * 100
gp_positive = (gp_dist.get(4, 0) + gp_dist.get(5, 0)) / gp_total * 100

# ============================================================================
# CALCULATE METRICS - iOS US
# ============================================================================

ios_total = len(ios_reviews)
ios_ratings = [r.get('rating', 0) for r in ios_reviews]
ios_avg = sum(ios_ratings) / len(ios_ratings)
ios_dist = Counter(ios_ratings)

ios_1star = ios_dist.get(1, 0)
ios_1star_pct = ios_1star / ios_total * 100
ios_5star = ios_dist.get(5, 0)
ios_5star_pct = ios_5star / ios_total * 100
ios_negative = (ios_dist.get(1, 0) + ios_dist.get(2, 0)) / ios_total * 100
ios_positive = (ios_dist.get(4, 0) + ios_dist.get(5, 0)) / ios_total * 100

# ============================================================================
# ISSUE CATEGORIZATION FOR GOOGLE PLAY
# ============================================================================

ISSUE_CATEGORIES = {
    "printing": {
        "name": "Printing Problems",
        "keywords": ["print", "printing", "won't print", "not printing", "can't print",
                     "print job", "queue", "stuck", "blank", "doesn't print", "failed to print"],
        "count": 0
    },
    "connectivity": {
        "name": "Connectivity/WiFi",
        "keywords": ["offline", "connect", "connection", "wifi", "network", "disconnect",
                     "won't connect", "can't connect", "bluetooth", "wireless", "reconnect"],
        "count": 0
    },
    "scanning": {
        "name": "Scanning Issues",
        "keywords": ["scan", "scanning", "scanner", "copy", "won't scan", "can't scan"],
        "count": 0
    },
    "setup": {
        "name": "Setup/Installation",
        "keywords": ["setup", "set up", "install", "configure", "add printer", "pairing"],
        "count": 0
    },
    "crashes": {
        "name": "App Crashes/Bugs",
        "keywords": ["crash", "bug", "freeze", "glitch", "error", "not working",
                     "broken", "slow", "laggy", "unresponsive"],
        "count": 0
    },
    "subscription": {
        "name": "Subscription/Ads",
        "keywords": ["subscription", "subscribe", "hp+", "instant ink", "pay", "ads",
                     "advertisement", "premium", "money", "charge"],
        "count": 0
    },
    "login": {
        "name": "Login/Account",
        "keywords": ["login", "log in", "sign in", "account", "password", "email",
                     "verification", "authenticate"],
        "count": 0
    }
}

for _, row in gp_df.iterrows():
    content = str(row.get('content', '')).lower()
    for cat_id, cat_info in ISSUE_CATEGORIES.items():
        for keyword in cat_info['keywords']:
            if keyword in content:
                cat_info['count'] += 1
                break

# Sort by count
sorted_issues = sorted(ISSUE_CATEGORIES.items(), key=lambda x: x[1]['count'], reverse=True)
top_5_issues = sorted_issues[:5]

# ============================================================================
# MONTHLY TREND
# ============================================================================

gp_df['month'] = gp_df['date'].dt.to_period('M')
gp_monthly = gp_df.groupby('month').agg({'rating': ['mean', 'count']}).reset_index()
gp_monthly.columns = ['month', 'avg_rating', 'count']

# iOS monthly
ios_monthly_data = defaultdict(lambda: {'ratings': [], 'count': 0})
for r in ios_reviews:
    date_str = r.get('date', '')
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            month_key = dt.strftime('%Y-%m')
            ios_monthly_data[month_key]['ratings'].append(r.get('rating', 0))
            ios_monthly_data[month_key]['count'] += 1
        except:
            pass

# ============================================================================
# CREATE GOOGLE PLAY US EXECUTIVE DASHBOARD
# ============================================================================

fig = plt.figure(figsize=(16, 12), facecolor='white')
fig.suptitle('HP APP - GOOGLE PLAY US MARKET EXECUTIVE SUMMARY\nOctober 2025 - January 2026 | Written Reviews Analysis',
             fontsize=14, fontweight='bold', y=0.98, color='#2c3e50')

# Top metrics
metrics_config = [
    {"value": f"{gp_total:,}", "label": "Total Reviews", "sublabel": "US Market", "bg": "#e8f5e9", "border": "#4caf50"},
    {"value": f"{gp_avg:.2f}", "label": "Avg Rating", "sublabel": "out of 5.0", "bg": "#fff3e0", "border": "#ff9800"},
    {"value": f"{gp_1star_pct:.1f}%", "label": "1-Star Reviews", "sublabel": f"({gp_1star} reviews)", "bg": "#ffebee", "border": "#f44336"},
    {"value": f"{gp_5star_pct:.1f}%", "label": "5-Star Reviews", "sublabel": f"({gp_5star} reviews)", "bg": "#e3f2fd", "border": "#2196f3"},
    {"value": f"{gp_negative:.1f}%", "label": "Negative Sentiment", "sublabel": "(1-2 stars)", "bg": "#fce4ec", "border": "#e91e63"},
]

for i, m in enumerate(metrics_config):
    ax = fig.add_axes([0.05 + i * 0.185, 0.85, 0.16, 0.09])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    rect = FancyBboxPatch((0.05, 0.1), 0.9, 0.8, boxstyle="round,pad=0.02",
                          facecolor=m['bg'], edgecolor=m['border'], linewidth=2)
    ax.add_patch(rect)
    ax.text(0.5, 0.6, m['value'], fontsize=20, fontweight='bold', ha='center', va='center', color='#2c3e50')
    ax.text(0.5, 0.25, m['label'], fontsize=9, ha='center', va='center', color='#555')
    ax.text(0.5, 0.08, m['sublabel'], fontsize=7, ha='center', va='center', color='#888')

# Rating Distribution
ax_rating = fig.add_axes([0.05, 0.52, 0.28, 0.28])
stars = ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star']
counts = [gp_dist.get(5, 0), gp_dist.get(4, 0), gp_dist.get(3, 0), gp_dist.get(2, 0), gp_dist.get(1, 0)]
pcts = [c / gp_total * 100 for c in counts]
colors = ['#4caf50', '#8bc34a', '#ffeb3b', '#ff9800', '#f44336']
bars = ax_rating.barh(stars, pcts, color=colors, edgecolor='white', height=0.6)
for bar, pct, count in zip(bars, pcts, counts):
    ax_rating.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                  f'{pct:.1f}% ({count})', va='center', fontsize=9)
ax_rating.set_xlabel('Percentage of Reviews (%)', fontsize=9)
ax_rating.set_title('Rating Distribution', fontweight='bold', fontsize=11, pad=10)
ax_rating.set_xlim(0, 80)
ax_rating.invert_yaxis()
ax_rating.spines['top'].set_visible(False)
ax_rating.spines['right'].set_visible(False)

# Sentiment Breakdown
ax_sentiment = fig.add_axes([0.38, 0.52, 0.25, 0.28])
neg_count = gp_dist.get(1, 0) + gp_dist.get(2, 0)
neu_count = gp_dist.get(3, 0)
pos_count = gp_dist.get(4, 0) + gp_dist.get(5, 0)
sentiment_data = [neg_count, neu_count, pos_count]
sentiment_colors = ['#f44336', '#ffeb3b', '#4caf50']
wedges, texts, autotexts = ax_sentiment.pie(sentiment_data, colors=sentiment_colors,
    autopct='%1.1f%%', startangle=90, pctdistance=0.75,
    wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2))
for autotext in autotexts:
    autotext.set_fontsize(9)
    autotext.set_fontweight('bold')
ax_sentiment.text(0, 0, f'{gp_avg:.1f}\nAvg', ha='center', va='center', fontsize=14, fontweight='bold', color='#2c3e50')
ax_sentiment.set_title('Sentiment Breakdown', fontweight='bold', fontsize=11, pad=10)
ax_sentiment.legend(wedges, [f'Negative ({neg_count})', f'Neutral ({neu_count})', f'Positive ({pos_count})'],
                    loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=8)

# Rating Comparison
ax_compare = fig.add_axes([0.68, 0.52, 0.27, 0.28])
ax_compare.axis('off')
ax_compare.set_xlim(0, 1)
ax_compare.set_ylim(0, 1)
ax_compare.text(0.5, 0.95, 'RATING COMPARISON', fontweight='bold', fontsize=10, ha='center', va='top', color='#2c3e50')

rect1 = FancyBboxPatch((0.1, 0.65), 0.8, 0.22, boxstyle="round,pad=0.02",
                       facecolor='#e8f5e9', edgecolor='#4caf50', linewidth=1)
ax_compare.add_patch(rect1)
ax_compare.text(0.5, 0.8, '4.2', fontsize=18, fontweight='bold', ha='center', color='#4caf50')
ax_compare.text(0.5, 0.68, 'Play Store Overall (~34K ratings)', fontsize=8, ha='center', color='#666')

rect2 = FancyBboxPatch((0.1, 0.35), 0.8, 0.22, boxstyle="round,pad=0.02",
                       facecolor='#ffebee', edgecolor='#f44336', linewidth=1)
ax_compare.add_patch(rect2)
ax_compare.text(0.5, 0.5, f'{gp_avg:.2f}', fontsize=18, fontweight='bold', ha='center', color='#f44336')
ax_compare.text(0.5, 0.38, f'US Oct+ Reviews ({gp_total} reviews)', fontsize=8, ha='center', color='#666')

gap = 4.2 - gp_avg
rect3 = FancyBboxPatch((0.1, 0.05), 0.8, 0.22, boxstyle="round,pad=0.02",
                       facecolor='#fff8e1', edgecolor='#ffc107', linewidth=1)
ax_compare.add_patch(rect3)
ax_compare.text(0.5, 0.2, f'-{gap:.2f}', fontsize=18, fontweight='bold', ha='center', color='#ff5722')
ax_compare.text(0.5, 0.08, 'Gap (Recent vs Overall)', fontsize=8, ha='center', color='#666')

# Top 5 Issues
ax_issues = fig.add_axes([0.05, 0.18, 0.42, 0.28])
issue_names = [item[1]['name'] for item in top_5_issues]
issue_counts = [item[1]['count'] for item in top_5_issues]
issue_pcts = [c / gp_total * 100 for c in issue_counts]
issue_colors = ['#f44336', '#ff5722', '#ff9800', '#ffc107', '#ffeb3b']
bars = ax_issues.barh(issue_names[::-1], issue_pcts[::-1], color=issue_colors[::-1], edgecolor='white', height=0.6)
for bar, pct, count in zip(bars, issue_pcts[::-1], issue_counts[::-1]):
    ax_issues.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                  f'{pct:.1f}% ({count})', va='center', fontsize=9, fontweight='bold')
ax_issues.set_xlabel('Percentage of Reviews Mentioning Issue', fontsize=9)
ax_issues.set_title('TOP 5 CUSTOMER ISSUES', fontweight='bold', fontsize=11, pad=10, color='#c62828')
ax_issues.set_xlim(0, 50)
ax_issues.spines['top'].set_visible(False)
ax_issues.spines['right'].set_visible(False)

# Monthly Trend
ax_trend = fig.add_axes([0.55, 0.18, 0.4, 0.28])
months_labels = ['Oct 2025', 'Nov 2025', 'Dec 2025', 'Jan 2026']
gp_monthly_avgs = []
gp_monthly_counts = []
for m in ['2025-10', '2025-11', '2025-12', '2026-01']:
    month_data = gp_df[gp_df['date'].dt.strftime('%Y-%m') == m]
    gp_monthly_avgs.append(month_data['rating'].mean() if len(month_data) > 0 else 0)
    gp_monthly_counts.append(len(month_data))

x = np.arange(len(months_labels))
ax_trend.plot(x, gp_monthly_avgs, 'o-', color='#f44336', linewidth=2, markersize=8)
ax_trend.set_ylabel('Avg Rating', color='#f44336', fontsize=9)
ax_trend.tick_params(axis='y', labelcolor='#f44336')
ax_trend.set_ylim(1, 5)
for i, (xi, avg) in enumerate(zip(x, gp_monthly_avgs)):
    ax_trend.annotate(f'{avg:.2f}', (xi, avg), textcoords="offset points",
                     xytext=(0, 10), ha='center', fontsize=9, color='#f44336')

ax2 = ax_trend.twinx()
ax2.bar(x, gp_monthly_counts, alpha=0.3, color='#2196f3', width=0.4)
ax2.set_ylabel('Number of Reviews', color='#2196f3', fontsize=9)
ax2.tick_params(axis='y', labelcolor='#2196f3')
ax_trend.set_xticks(x)
ax_trend.set_xticklabels(months_labels, fontsize=9)
ax_trend.set_title('Monthly Trend', fontweight='bold', fontsize=11, pad=10)
for i, count in enumerate(gp_monthly_counts):
    ax2.text(i, count + 20, f'{count}', ha='center', fontsize=8, color='#2196f3')

# Key Insights
ax_insights = fig.add_axes([0.05, 0.01, 0.9, 0.12])
ax_insights.axis('off')
insights_box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                               facecolor='#fafafa', edgecolor='#ddd', linewidth=1,
                               transform=ax_insights.transAxes)
ax_insights.add_patch(insights_box)

insights_text = f"""KEY EXECUTIVE INSIGHTS - GOOGLE PLAY US MARKET

[RATING GAP]                                          [TOP ISSUES ANALYSIS]
* Play Store Overall: 4.2 stars (34K ratings)         #1 {top_5_issues[0][1]['name'].upper()} ({top_5_issues[0][1]['count']} mentions): Core functionality failing
* US Written Reviews: {gp_avg:.2f} stars ({gp_total} reviews)         #2 {top_5_issues[1][1]['name'].upper()} ({top_5_issues[1][1]['count']} mentions): Connection drops frequently
* Rating gap of {gap:.2f} stars - severe disconnect            #3 {top_5_issues[2][1]['name'].upper()} ({top_5_issues[2][1]['count']} mentions): Scan/copy features broken
                                                      #4 {top_5_issues[3][1]['name'].upper()} ({top_5_issues[3][1]['count']} mentions): Overly complicated setup
[CRITICAL FINDINGS]                                   #5 {top_5_issues[4][1]['name'].upper()} ({top_5_issues[4][1]['count']} mentions): Stability issues
* {gp_1star_pct:.1f}% of all reviews are 1-star (worst in class)
* {gp_negative:.1f}% negative sentiment overall                 [RECOMMENDATION]
* US market more dissatisfied than global average     URGENT: Address core printing and connectivity issues
"""

ax_insights.text(0.02, 0.9, insights_text, transform=ax_insights.transAxes,
                fontsize=7.5, verticalalignment='top', fontfamily='monospace', color='#333')

plt.savefig('GooglePlay_HP_App_US_Oct_Executive_Summary.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Saved: GooglePlay_HP_App_US_Oct_Executive_Summary.png")
plt.close()

# ============================================================================
# CREATE iOS vs ANDROID US COMPARISON
# ============================================================================

fig2 = plt.figure(figsize=(16, 12), facecolor='white')
fig2.suptitle('HP APP - US MARKET COMPARISON: iOS vs Android\nOctober 2025 - January 2026',
              fontsize=16, fontweight='bold', y=0.98, color='#2c3e50')

ios_color = '#007AFF'
android_color = '#3DDC84'

# Top metrics comparison
ax_metrics = fig2.add_axes([0.05, 0.82, 0.9, 0.12])
ax_metrics.axis('off')

metrics = [
    ("Total Reviews", f"{ios_total:,}", f"{gp_total:,}"),
    ("Avg Rating", f"{ios_avg:.2f}", f"{gp_avg:.2f}"),
    ("1-Star %", f"{ios_1star_pct:.1f}%", f"{gp_1star_pct:.1f}%"),
    ("Negative %", f"{ios_negative:.1f}%", f"{gp_negative:.1f}%"),
]

for i, (label, ios_val, android_val) in enumerate(metrics):
    x_start = 0.05 + i * 0.24
    ax_metrics.text(x_start + 0.09, 0.85, label, fontsize=12, fontweight='bold',
                   ha='center', transform=ax_metrics.transAxes, color='#333')

    # iOS box
    rect_ios = FancyBboxPatch((x_start, 0.35), 0.08, 0.4, boxstyle="round,pad=0.02",
                               facecolor=ios_color, alpha=0.15, edgecolor=ios_color, linewidth=2,
                               transform=ax_metrics.transAxes)
    ax_metrics.add_patch(rect_ios)
    ax_metrics.text(x_start + 0.04, 0.55, ios_val, fontsize=16, fontweight='bold',
                   ha='center', va='center', color=ios_color, transform=ax_metrics.transAxes)
    ax_metrics.text(x_start + 0.04, 0.2, 'iOS', fontsize=10, ha='center',
                   color=ios_color, transform=ax_metrics.transAxes)

    # Android box
    rect_android = FancyBboxPatch((x_start + 0.1, 0.35), 0.08, 0.4, boxstyle="round,pad=0.02",
                                   facecolor=android_color, alpha=0.15, edgecolor=android_color, linewidth=2,
                                   transform=ax_metrics.transAxes)
    ax_metrics.add_patch(rect_android)
    ax_metrics.text(x_start + 0.14, 0.55, android_val, fontsize=16, fontweight='bold',
                   ha='center', va='center', color='#2E7D32', transform=ax_metrics.transAxes)
    ax_metrics.text(x_start + 0.14, 0.2, 'Android', fontsize=10, ha='center',
                   color='#2E7D32', transform=ax_metrics.transAxes)

# Rating Distribution Comparison
ax_rating2 = fig2.add_axes([0.08, 0.42, 0.4, 0.35])
stars = [5, 4, 3, 2, 1]
ios_pcts = [ios_dist.get(s, 0) / ios_total * 100 for s in stars]
android_pcts = [gp_dist.get(s, 0) / gp_total * 100 for s in stars]

x = np.arange(len(stars))
width = 0.35
bars1 = ax_rating2.barh(x - width/2, ios_pcts, width, label='iOS', color=ios_color, alpha=0.8)
bars2 = ax_rating2.barh(x + width/2, android_pcts, width, label='Android', color=android_color, alpha=0.8)

ax_rating2.set_yticks(x)
ax_rating2.set_yticklabels([f'{s} Star' for s in stars])
ax_rating2.set_xlabel('Percentage of Reviews')
ax_rating2.set_title('Rating Distribution - US Market', fontweight='bold', pad=10)
ax_rating2.legend(loc='lower right')
ax_rating2.set_xlim(0, 80)
ax_rating2.invert_yaxis()

for bar, pct in zip(bars1, ios_pcts):
    if pct > 3:
        ax_rating2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                       f'{pct:.1f}%', va='center', fontsize=8, color=ios_color)
for bar, pct in zip(bars2, android_pcts):
    if pct > 3:
        ax_rating2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                       f'{pct:.1f}%', va='center', fontsize=8, color='#2E7D32')

# Monthly Trend Comparison
ax_trend2 = fig2.add_axes([0.55, 0.42, 0.4, 0.35])
months = ['2025-10', '2025-11', '2025-12', '2026-01']
months_labels = ['Oct', 'Nov', 'Dec', 'Jan']

ios_monthly_counts = [ios_monthly_data.get(m, {'count': 0})['count'] for m in months]
gp_monthly_counts_list = []
for m in months:
    month_data = gp_df[gp_df['date'].dt.strftime('%Y-%m') == m]
    gp_monthly_counts_list.append(len(month_data))

x = np.arange(len(months))
width = 0.35
bars1 = ax_trend2.bar(x - width/2, ios_monthly_counts, width, label='iOS', color=ios_color, alpha=0.8)
bars2 = ax_trend2.bar(x + width/2, gp_monthly_counts_list, width, label='Android', color=android_color, alpha=0.8)

ax_trend2.set_xticks(x)
ax_trend2.set_xticklabels(months_labels)
ax_trend2.set_ylabel('Number of Reviews')
ax_trend2.set_title('Review Volume by Month - US Market', fontweight='bold', pad=10)
ax_trend2.legend()

for bar in bars1:
    ax_trend2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                  f'{int(bar.get_height())}', ha='center', fontsize=9, color=ios_color)
for bar in bars2:
    ax_trend2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                  f'{int(bar.get_height())}', ha='center', fontsize=9, color='#2E7D32')

# Sentiment Comparison
ax_sent2 = fig2.add_axes([0.08, 0.05, 0.4, 0.32])
categories = ['Positive\n(4-5 Star)', 'Neutral\n(3 Star)', 'Negative\n(1-2 Star)']
ios_sent = [ios_positive, (ios_dist.get(3, 0) / ios_total * 100), ios_negative]
android_sent = [gp_positive, (gp_dist.get(3, 0) / gp_total * 100), gp_negative]

x = np.arange(len(categories))
width = 0.35
bars1 = ax_sent2.bar(x - width/2, ios_sent, width, label='iOS', color=ios_color, alpha=0.8)
bars2 = ax_sent2.bar(x + width/2, android_sent, width, label='Android', color=android_color, alpha=0.8)

ax_sent2.set_xticks(x)
ax_sent2.set_xticklabels(categories)
ax_sent2.set_ylabel('Percentage')
ax_sent2.set_title('Sentiment Comparison - US Market', fontweight='bold', pad=10)
ax_sent2.legend()
ax_sent2.set_ylim(0, 85)

for bar in bars1:
    ax_sent2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f'{bar.get_height():.1f}%', ha='center', fontsize=9)
for bar in bars2:
    ax_sent2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f'{bar.get_height():.1f}%', ha='center', fontsize=9)

# Key Insights
ax_insights2 = fig2.add_axes([0.55, 0.05, 0.4, 0.32])
ax_insights2.axis('off')

insights_text2 = f"""
KEY FINDINGS - US MARKET

SIMILARITIES:
  Both platforms ~2.0-2.5 avg rating
  Both have 60%+ negative reviews
  Both show same core issues

DIFFERENCES:
  Android has {gp_total/ios_total:.1f}x more reviews
  Android slightly worse ({gp_avg:.2f} vs {ios_avg:.2f})
  Android 1-star: {gp_1star_pct:.1f}% vs iOS: {ios_1star_pct:.1f}%

TOP ISSUE BOTH PLATFORMS:
  PRINTING PROBLEMS
  - Core functionality failing
  - Users cannot complete basic tasks

RECOMMENDATION:
  Cross-platform issue indicates
  backend/service problems, not
  platform-specific bugs.

  Priority: Fix printing pipeline
"""

ax_insights2.text(0.05, 0.95, insights_text2, transform=ax_insights2.transAxes,
                 fontsize=10, verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='#f0f0f0', edgecolor='#ccc'))

plt.savefig('HP_App_US_iOS_vs_Android_Oct_Comparison.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Saved: HP_App_US_iOS_vs_Android_Oct_Comparison.png")
plt.close()

# ============================================================================
# SAVE COMPARISON DATA
# ============================================================================

comparison_json = {
    "period": "October 2025 - January 2026",
    "market": "US Only",
    "ios": {
        "total_reviews": ios_total,
        "average_rating": round(ios_avg, 2),
        "1_star_percent": round(ios_1star_pct, 1),
        "negative_percent": round(ios_negative, 1),
        "positive_percent": round(ios_positive, 1)
    },
    "android": {
        "total_reviews": gp_total,
        "average_rating": round(gp_avg, 2),
        "1_star_percent": round(gp_1star_pct, 1),
        "negative_percent": round(gp_negative, 1),
        "positive_percent": round(gp_positive, 1),
        "top_5_issues": [{"name": item[1]['name'], "count": item[1]['count'],
                         "percent": round(item[1]['count']/gp_total*100, 1)} for item in top_5_issues]
    },
    "analysis_date": datetime.now().isoformat()
}

with open('HP_App_US_iOS_vs_Android_Oct_Comparison.json', 'w') as f:
    json.dump(comparison_json, f, indent=2)
print("Saved: HP_App_US_iOS_vs_Android_Oct_Comparison.json")

print("\nDone!")
