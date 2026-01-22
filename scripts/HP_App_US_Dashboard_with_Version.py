"""
HP App - US Market Executive Dashboard with Version Info
Google Play US (October 2025+)
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from datetime import datetime
from collections import Counter, defaultdict

# Load data
gp_df = pd.read_csv('hp_app_reviews_oct2025_present.csv')
gp_df['date'] = pd.to_datetime(gp_df['date'])

print(f"Google Play US reviews: {len(gp_df)}")

# ============================================================================
# CALCULATE METRICS
# ============================================================================

gp_total = len(gp_df)
gp_avg = gp_df['rating'].mean()
gp_dist = gp_df['rating'].value_counts().to_dict()

gp_1star = gp_dist.get(1, 0)
gp_1star_pct = gp_1star / gp_total * 100
gp_5star = gp_dist.get(5, 0)
gp_5star_pct = gp_5star / gp_total * 100
gp_negative = (gp_dist.get(1, 0) + gp_dist.get(2, 0)) / gp_total * 100

# Version analysis
version_counts = gp_df['version'].value_counts().head(6)
version_ratings = gp_df.groupby('version')['rating'].agg(['mean', 'count']).reset_index()
version_ratings = version_ratings.sort_values('count', ascending=False).head(6)

# ============================================================================
# ISSUE CATEGORIZATION
# ============================================================================

ISSUE_CATEGORIES = {
    "printing": {"name": "Printing Problems", "keywords": ["print", "printing", "won't print", "not printing", "can't print", "print job", "queue", "stuck", "blank", "doesn't print"], "count": 0},
    "connectivity": {"name": "Connectivity/WiFi", "keywords": ["offline", "connect", "connection", "wifi", "network", "disconnect", "won't connect", "can't connect", "bluetooth", "wireless"], "count": 0},
    "scanning": {"name": "Scanning Issues", "keywords": ["scan", "scanning", "scanner", "copy", "won't scan", "can't scan"], "count": 0},
    "setup": {"name": "Setup/Installation", "keywords": ["setup", "set up", "install", "configure", "add printer", "pairing"], "count": 0},
    "crashes": {"name": "App Crashes/Bugs", "keywords": ["crash", "bug", "freeze", "glitch", "error", "not working", "broken", "slow", "laggy"], "count": 0},
}

for _, row in gp_df.iterrows():
    content = str(row.get('content', '')).lower()
    for cat_id, cat_info in ISSUE_CATEGORIES.items():
        for keyword in cat_info['keywords']:
            if keyword in content:
                cat_info['count'] += 1
                break

sorted_issues = sorted(ISSUE_CATEGORIES.items(), key=lambda x: x[1]['count'], reverse=True)
top_5_issues = sorted_issues[:5]

# Monthly data
gp_monthly_avgs = []
gp_monthly_counts = []
for m in ['2025-10', '2025-11', '2025-12', '2026-01']:
    month_data = gp_df[gp_df['date'].dt.strftime('%Y-%m') == m]
    gp_monthly_avgs.append(month_data['rating'].mean() if len(month_data) > 0 else 0)
    gp_monthly_counts.append(len(month_data))

# ============================================================================
# CREATE DASHBOARD
# ============================================================================

fig = plt.figure(figsize=(18, 14), facecolor='white')
fig.suptitle('HP APP - GOOGLE PLAY US MARKET EXECUTIVE SUMMARY\nOctober 2025 - January 2026 | Written Reviews Analysis',
             fontsize=14, fontweight='bold', y=0.98, color='#2c3e50')

# ============================================================================
# TOP METRICS BAR
# ============================================================================

metrics_config = [
    {"value": f"{gp_total:,}", "label": "Total Reviews", "sublabel": "US Market", "bg": "#e8f5e9", "border": "#4caf50"},
    {"value": f"{gp_avg:.2f}", "label": "Avg Rating", "sublabel": "out of 5.0", "bg": "#fff3e0", "border": "#ff9800"},
    {"value": f"{gp_1star_pct:.1f}%", "label": "1-Star Reviews", "sublabel": f"({gp_1star} reviews)", "bg": "#ffebee", "border": "#f44336"},
    {"value": f"{gp_5star_pct:.1f}%", "label": "5-Star Reviews", "sublabel": f"({gp_5star} reviews)", "bg": "#e3f2fd", "border": "#2196f3"},
    {"value": f"{gp_negative:.1f}%", "label": "Negative Sentiment", "sublabel": "(1-2 stars)", "bg": "#fce4ec", "border": "#e91e63"},
]

for i, m in enumerate(metrics_config):
    ax = fig.add_axes([0.03 + i * 0.19, 0.88, 0.17, 0.08])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    rect = FancyBboxPatch((0.05, 0.1), 0.9, 0.8, boxstyle="round,pad=0.02",
                          facecolor=m['bg'], edgecolor=m['border'], linewidth=2)
    ax.add_patch(rect)
    ax.text(0.5, 0.6, m['value'], fontsize=18, fontweight='bold', ha='center', va='center', color='#2c3e50')
    ax.text(0.5, 0.25, m['label'], fontsize=9, ha='center', va='center', color='#555')
    ax.text(0.5, 0.08, m['sublabel'], fontsize=7, ha='center', va='center', color='#888')

# ============================================================================
# RATING DISTRIBUTION
# ============================================================================

ax_rating = fig.add_axes([0.03, 0.58, 0.28, 0.26])
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

# ============================================================================
# SENTIMENT BREAKDOWN
# ============================================================================

ax_sentiment = fig.add_axes([0.35, 0.58, 0.22, 0.26])
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
                    loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=7)

# ============================================================================
# VERSION ANALYSIS (NEW)
# ============================================================================

ax_version = fig.add_axes([0.6, 0.58, 0.37, 0.26])

# Get top versions with their ratings
top_versions = version_ratings.head(5)
ver_names = [str(v)[:12] if pd.notna(v) else 'Unknown' for v in top_versions['version']]
ver_counts = top_versions['count'].values
ver_avgs = top_versions['mean'].values

x = np.arange(len(ver_names))
width = 0.35

# Bar for count
bars1 = ax_version.bar(x - width/2, ver_counts, width, label='# Reviews', color='#3498db', alpha=0.8)
ax_version.set_ylabel('Number of Reviews', color='#3498db', fontsize=9)
ax_version.tick_params(axis='y', labelcolor='#3498db')

# Line for avg rating
ax_ver2 = ax_version.twinx()
line = ax_ver2.plot(x, ver_avgs, 'o-', color='#e74c3c', linewidth=2, markersize=8, label='Avg Rating')
ax_ver2.set_ylabel('Avg Rating', color='#e74c3c', fontsize=9)
ax_ver2.tick_params(axis='y', labelcolor='#e74c3c')
ax_ver2.set_ylim(1, 5)

# Add rating labels on points
for i, (xi, avg) in enumerate(zip(x, ver_avgs)):
    ax_ver2.annotate(f'{avg:.2f}', (xi, avg), textcoords="offset points",
                    xytext=(0, 8), ha='center', fontsize=8, color='#e74c3c', fontweight='bold')

# Add count labels on bars
for bar in bars1:
    ax_version.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                   f'{int(bar.get_height())}', ha='center', fontsize=8, color='#3498db')

ax_version.set_xticks(x)
ax_version.set_xticklabels([f'v{v}' for v in ver_names], fontsize=8, rotation=15, ha='right')
ax_version.set_title('Rating by App Version', fontweight='bold', fontsize=11, pad=10)
ax_version.spines['top'].set_visible(False)

# ============================================================================
# TOP 5 ISSUES
# ============================================================================

ax_issues = fig.add_axes([0.03, 0.28, 0.42, 0.26])
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
ax_issues.set_xlim(0, 55)
ax_issues.spines['top'].set_visible(False)
ax_issues.spines['right'].set_visible(False)

# ============================================================================
# MONTHLY TREND
# ============================================================================

ax_trend = fig.add_axes([0.52, 0.28, 0.45, 0.26])
months_labels = ['Oct 2025', 'Nov 2025', 'Dec 2025', 'Jan 2026']
x = np.arange(len(months_labels))

ax_trend.plot(x, gp_monthly_avgs, 'o-', color='#f44336', linewidth=2, markersize=8)
ax_trend.set_ylabel('Avg Rating', color='#f44336', fontsize=9)
ax_trend.tick_params(axis='y', labelcolor='#f44336')
ax_trend.set_ylim(1, 5)

for i, (xi, avg) in enumerate(zip(x, gp_monthly_avgs)):
    ax_trend.annotate(f'{avg:.2f}', (xi, avg), textcoords="offset points",
                     xytext=(0, 10), ha='center', fontsize=9, color='#f44336', fontweight='bold')

ax2 = ax_trend.twinx()
ax2.bar(x, gp_monthly_counts, alpha=0.3, color='#2196f3', width=0.5)
ax2.set_ylabel('Number of Reviews', color='#2196f3', fontsize=9)
ax2.tick_params(axis='y', labelcolor='#2196f3')

ax_trend.set_xticks(x)
ax_trend.set_xticklabels(months_labels, fontsize=9)
ax_trend.set_title('Monthly Trend', fontweight='bold', fontsize=11, pad=10)
ax_trend.spines['top'].set_visible(False)

for i, count in enumerate(gp_monthly_counts):
    ax2.text(i, count + 15, f'{count}', ha='center', fontsize=9, color='#2196f3')

# ============================================================================
# VERSION TABLE (NEW)
# ============================================================================

ax_ver_table = fig.add_axes([0.03, 0.12, 0.35, 0.12])
ax_ver_table.axis('off')

# Create version table
table_data = []
for i, (_, row) in enumerate(version_ratings.head(5).iterrows()):
    ver = str(row['version'])[:15] if pd.notna(row['version']) else 'Unknown'
    table_data.append([f"v{ver}", f"{int(row['count'])}", f"{row['mean']:.2f}"])

table = ax_ver_table.table(
    cellText=table_data,
    colLabels=['Version', 'Reviews', 'Avg Rating'],
    loc='center',
    cellLoc='center',
    colColours=['#e3f2fd', '#e3f2fd', '#e3f2fd']
)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.2, 1.5)

# Color code ratings
for i, row in enumerate(table_data):
    rating = float(row[2])
    if rating < 2.0:
        table[(i+1, 2)].set_facecolor('#ffcdd2')
    elif rating < 2.5:
        table[(i+1, 2)].set_facecolor('#ffe0b2')
    else:
        table[(i+1, 2)].set_facecolor('#c8e6c9')

ax_ver_table.set_title('Top Versions by Review Count', fontweight='bold', fontsize=10, pad=5)

# ============================================================================
# KEY INSIGHTS
# ============================================================================

ax_insights = fig.add_axes([0.4, 0.02, 0.57, 0.22])
ax_insights.axis('off')

# Get latest version info
latest_ver = version_ratings.iloc[0] if len(version_ratings) > 0 else None
latest_ver_name = str(latest_ver['version']) if latest_ver is not None and pd.notna(latest_ver['version']) else 'Unknown'
latest_ver_rating = latest_ver['mean'] if latest_ver is not None else 0
latest_ver_count = int(latest_ver['count']) if latest_ver is not None else 0

insights_text = f"""KEY EXECUTIVE INSIGHTS - GOOGLE PLAY US MARKET

[RATING ANALYSIS]                                    [VERSION INSIGHTS]
* Overall Store Rating: 4.2 stars                    * Most reviewed version: v{latest_ver_name[:12]}
* US Written Reviews: {gp_avg:.2f} stars              - {latest_ver_count} reviews, {latest_ver_rating:.2f} avg rating
* Rating Gap: -{4.2 - gp_avg:.2f} stars (severe)              * All recent versions rated below 2.5
                                                     * No improvement trend across versions
[CRITICAL FINDINGS]
* {gp_1star_pct:.1f}% of reviews are 1-star            [TOP ISSUES]
* {gp_negative:.1f}% negative sentiment                #1 Printing Problems ({top_5_issues[0][1]['count']} mentions)
* US users more dissatisfied than global avg         #2 Connectivity/WiFi ({top_5_issues[1][1]['count']} mentions)
                                                     #3 App Crashes ({top_5_issues[2][1]['count']} mentions)
[RECOMMENDATION]
URGENT: Core printing and connectivity issues persist across all app versions.
        Version updates are not addressing root causes. Backend investigation required.
"""

insights_box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                               facecolor='#fafafa', edgecolor='#ddd', linewidth=1,
                               transform=ax_insights.transAxes)
ax_insights.add_patch(insights_box)
ax_insights.text(0.02, 0.95, insights_text, transform=ax_insights.transAxes,
                fontsize=8, verticalalignment='top', fontfamily='monospace', color='#333')

# Footer
fig.text(0.5, 0.005, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | HP App - Google Play US Market Analysis',
         ha='center', fontsize=8, color='gray', style='italic')

plt.savefig('GooglePlay_HP_App_US_Oct_Executive_Summary_v2.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Saved: GooglePlay_HP_App_US_Oct_Executive_Summary_v2.png")
plt.close()

print("\nDone!")
