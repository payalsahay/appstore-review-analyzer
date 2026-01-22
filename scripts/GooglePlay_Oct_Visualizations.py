"""
Google Play HP App - October 2025+ Visualizations
Executive Dashboard for Product Manager
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.titleweight'] = 'bold'

# Load data
with open("GooglePlay_HP_Oct_Analytics.json", "r") as f:
    analytics = json.load(f)

with open("GooglePlay_HP_Oct_TopIssues.json", "r") as f:
    issues_data = json.load(f)

# ============================================================================
# CREATE EXECUTIVE DASHBOARD
# ============================================================================

fig = plt.figure(figsize=(16, 12))
fig.suptitle('HP Smart App - Google Play Store Analysis\nOctober 2025 - January 2026',
             fontsize=16, fontweight='bold', y=0.98)

# Color scheme
colors_rating = ['#2ecc71', '#87d068', '#f4d03f', '#e67e22', '#e74c3c']  # 5 to 1 stars
colors_issues = ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#9b59b6']

# ============================================================================
# 1. KEY METRICS PANEL (Top)
# ============================================================================
ax_metrics = fig.add_axes([0.05, 0.85, 0.9, 0.10])
ax_metrics.axis('off')

total_reviews = analytics['total_reviews']
avg_rating = analytics['average_rating']
one_star_pct = analytics['rating_distribution'].get('1', 0) / total_reviews * 100
five_star_pct = analytics['rating_distribution'].get('5', 0) / total_reviews * 100

metrics_text = f"""
┌────────────────────┬────────────────────┬────────────────────┬────────────────────┐
│   Total Reviews    │   Average Rating   │   1-Star Reviews   │   5-Star Reviews   │
│       {total_reviews:,}         │      {avg_rating:.2f} / 5.0      │      {one_star_pct:.1f}%          │       {five_star_pct:.1f}%         │
└────────────────────┴────────────────────┴────────────────────┴────────────────────┘
"""

# Create metric boxes
metric_data = [
    (f"{total_reviews:,}", "Total Reviews", "#3498db"),
    (f"{avg_rating:.2f}/5.0", "Avg Rating", "#e74c3c"),
    (f"{one_star_pct:.1f}%", "1-Star Reviews", "#c0392b"),
    (f"{five_star_pct:.1f}%", "5-Star Reviews", "#27ae60"),
]

for i, (value, label, color) in enumerate(metric_data):
    x_pos = 0.1 + i * 0.22
    # Box
    rect = mpatches.FancyBboxPatch((x_pos, 0.2), 0.18, 0.6,
                                    boxstyle="round,pad=0.02",
                                    facecolor=color, alpha=0.15,
                                    edgecolor=color, linewidth=2,
                                    transform=ax_metrics.transAxes)
    ax_metrics.add_patch(rect)
    # Value
    ax_metrics.text(x_pos + 0.09, 0.55, value, fontsize=18, fontweight='bold',
                   ha='center', va='center', color=color, transform=ax_metrics.transAxes)
    # Label
    ax_metrics.text(x_pos + 0.09, 0.3, label, fontsize=10,
                   ha='center', va='center', color='#555', transform=ax_metrics.transAxes)

# ============================================================================
# 2. RATING DISTRIBUTION (Left)
# ============================================================================
ax_rating = fig.add_subplot(2, 2, 1)
ax_rating.set_position([0.05, 0.45, 0.4, 0.35])

rating_dist = analytics['rating_distribution']
stars = [5, 4, 3, 2, 1]
counts = [rating_dist.get(str(s), 0) for s in stars]
percentages = [c / total_reviews * 100 for c in counts]

bars = ax_rating.barh([f'{s}★' for s in stars], percentages, color=colors_rating, edgecolor='white', height=0.6)

# Add percentage labels
for bar, pct, count in zip(bars, percentages, counts):
    width = bar.get_width()
    ax_rating.text(width + 1, bar.get_y() + bar.get_height()/2,
                  f'{pct:.1f}% ({count:,})', va='center', fontsize=10)

ax_rating.set_xlabel('Percentage of Reviews', fontsize=11)
ax_rating.set_title('Rating Distribution', pad=10)
ax_rating.set_xlim(0, 70)
ax_rating.invert_yaxis()

# Add severity indicator
ax_rating.axvline(x=50, color='red', linestyle='--', alpha=0.5, linewidth=1)
ax_rating.text(51, 4, 'Critical\nThreshold', fontsize=8, color='red', alpha=0.7)

# ============================================================================
# 3. TOP 5 ISSUES (Right)
# ============================================================================
ax_issues = fig.add_subplot(2, 2, 2)
ax_issues.set_position([0.55, 0.45, 0.4, 0.35])

top_issues = issues_data['top_5_issues']
issue_names = [issue['issue'].replace(' / ', '\n').replace(' Problems', '').replace(' Issues', '')
               for issue in top_issues]
issue_counts = [issue['mention_count'] for issue in top_issues]
issue_pcts = [issue['percentage'] for issue in top_issues]

# Horizontal bar chart
y_pos = np.arange(len(issue_names))
bars = ax_issues.barh(y_pos, issue_pcts, color=colors_issues, edgecolor='white', height=0.6)

# Add labels
for bar, pct, count in zip(bars, issue_pcts, issue_counts):
    width = bar.get_width()
    ax_issues.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                  f'{pct:.1f}% ({count:,})', va='center', fontsize=9)

ax_issues.set_yticks(y_pos)
ax_issues.set_yticklabels(issue_names, fontsize=9)
ax_issues.set_xlabel('Percentage of Reviews Mentioning Issue', fontsize=11)
ax_issues.set_title('Top 5 User Pain Points', pad=10)
ax_issues.set_xlim(0, 35)
ax_issues.invert_yaxis()

# ============================================================================
# 4. ISSUE IMPACT TREEMAP-STYLE (Bottom Left)
# ============================================================================
ax_treemap = fig.add_subplot(2, 2, 3)
ax_treemap.set_position([0.05, 0.05, 0.4, 0.35])
ax_treemap.axis('off')
ax_treemap.set_title('Issue Severity Matrix', pad=10)

# Create a simple grid representation
issue_short_names = ['Printing\nFails', 'Goes\nOffline', 'Scanning\nBroken', 'Setup\nHard', 'App\nCrashes']
issue_impacts = [1445, 698, 474, 394, 375]

# Normalize for sizing
max_impact = max(issue_impacts)
sizes = [impact / max_impact for impact in issue_impacts]

# Create boxes
x_positions = [0.1, 0.55, 0.1, 0.55, 0.33]
y_positions = [0.55, 0.55, 0.1, 0.1, 0.32]
widths = [0.4 * s + 0.15 for s in sizes]
heights = [0.35 * s + 0.1 for s in sizes]

for i, (name, impact, color) in enumerate(zip(issue_short_names, issue_impacts, colors_issues)):
    x = x_positions[i]
    y = y_positions[i]
    w = widths[i]
    h = heights[i]

    rect = mpatches.FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.02",
                                    facecolor=color, alpha=0.8,
                                    edgecolor='white', linewidth=2,
                                    transform=ax_treemap.transAxes)
    ax_treemap.add_patch(rect)

    # Text
    ax_treemap.text(x + w/2, y + h/2 + 0.02, name, fontsize=10, fontweight='bold',
                   ha='center', va='center', color='white', transform=ax_treemap.transAxes)
    ax_treemap.text(x + w/2, y + h/2 - 0.08, f'{impact:,}', fontsize=9,
                   ha='center', va='center', color='white', transform=ax_treemap.transAxes)

# ============================================================================
# 5. SENTIMENT GAUGE (Bottom Right)
# ============================================================================
ax_gauge = fig.add_subplot(2, 2, 4)
ax_gauge.set_position([0.55, 0.05, 0.4, 0.35])

# Create a donut chart showing positive vs negative
negative_reviews = sum(rating_dist.get(str(s), 0) for s in [1, 2])
neutral_reviews = rating_dist.get('3', 0)
positive_reviews = sum(rating_dist.get(str(s), 0) for s in [4, 5])

sentiment_data = [negative_reviews, neutral_reviews, positive_reviews]
sentiment_labels = ['Negative\n(1-2★)', 'Neutral\n(3★)', 'Positive\n(4-5★)']
sentiment_colors = ['#e74c3c', '#f39c12', '#27ae60']

# Donut chart
wedges, texts, autotexts = ax_gauge.pie(sentiment_data,
                                         labels=sentiment_labels,
                                         colors=sentiment_colors,
                                         autopct='%1.1f%%',
                                         startangle=90,
                                         pctdistance=0.75,
                                         wedgeprops=dict(width=0.5, edgecolor='white'))

# Style the percentage text
for autotext in autotexts:
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

# Center text
ax_gauge.text(0, 0, f'Overall\nSentiment', ha='center', va='center',
              fontsize=11, fontweight='bold', color='#333')

ax_gauge.set_title('User Sentiment Breakdown', pad=10)

# ============================================================================
# FOOTER
# ============================================================================
fig.text(0.5, 0.01, f'Analysis generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Data source: Google Play Store | Package: com.hp.printercontrol',
         ha='center', fontsize=9, color='gray', style='italic')

# Save
plt.savefig('GooglePlay_HP_Oct_Dashboard.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✅ Saved: GooglePlay_HP_Oct_Dashboard.png")

plt.close()

# ============================================================================
# CREATE DETAILED ISSUES CHART
# ============================================================================

fig2, ax = plt.subplots(figsize=(12, 8))

# All issue categories
all_issues = issues_data['all_issue_categories']
sorted_issues = sorted(all_issues.items(), key=lambda x: x[1]['count'], reverse=True)

names = [item[1]['name'] for item in sorted_issues if item[1]['count'] > 0]
counts = [item[1]['count'] for item in sorted_issues if item[1]['count'] > 0]
pcts = [item[1]['percentage'] for item in sorted_issues if item[1]['count'] > 0]

# Color gradient
colors_gradient = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(names)))

y_pos = np.arange(len(names))
bars = ax.barh(y_pos, counts, color=colors_gradient, edgecolor='white', height=0.7)

# Add labels
for bar, pct, count in zip(bars, pcts, counts):
    width = bar.get_width()
    ax.text(width + 20, bar.get_y() + bar.get_height()/2,
           f'{count:,} ({pct:.1f}%)', va='center', fontsize=10)

ax.set_yticks(y_pos)
ax.set_yticklabels(names, fontsize=10)
ax.set_xlabel('Number of Reviews Mentioning Issue', fontsize=12)
ax.set_title('HP Smart App (Google Play) - All User Issues\nOctober 2025 - January 2026',
             fontsize=14, fontweight='bold', pad=15)
ax.invert_yaxis()
ax.set_xlim(0, max(counts) * 1.3)

# Add priority zones
ax.axvline(x=500, color='red', linestyle='--', alpha=0.3, linewidth=1)
ax.axvline(x=300, color='orange', linestyle='--', alpha=0.3, linewidth=1)
ax.text(510, len(names)-0.5, 'High Priority', fontsize=8, color='red', alpha=0.7)
ax.text(310, len(names)-0.5, 'Medium Priority', fontsize=8, color='orange', alpha=0.7)

plt.tight_layout()
plt.savefig('GooglePlay_HP_Oct_AllIssues.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✅ Saved: GooglePlay_HP_Oct_AllIssues.png")

plt.close()

print("\n📊 Visualizations complete!")
