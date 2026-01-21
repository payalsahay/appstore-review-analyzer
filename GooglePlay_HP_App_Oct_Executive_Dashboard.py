"""
Google Play HP App - Executive Summary Dashboard
Matching iOS style
October 2025 - January 2026
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from datetime import datetime
from collections import Counter, defaultdict

# Load data
with open('GooglePlay_HP_App_Oct_Reviews.json', 'r') as f:
    reviews = json.load(f)

with open('GooglePlay_HP_App_Oct_TopIssues.json', 'r') as f:
    issues_data = json.load(f)

# ============================================================================
# CALCULATE METRICS
# ============================================================================

total_reviews = len(reviews)
ratings = [r.get('rating', 0) for r in reviews]
avg_rating = sum(ratings) / len(ratings)
rating_dist = Counter(ratings)

one_star_count = rating_dist.get(1, 0)
one_star_pct = one_star_count / total_reviews * 100

five_star_count = rating_dist.get(5, 0)
five_star_pct = five_star_count / total_reviews * 100

negative_count = rating_dist.get(1, 0) + rating_dist.get(2, 0)
negative_pct = negative_count / total_reviews * 100

positive_count = rating_dist.get(4, 0) + rating_dist.get(5, 0)
neutral_count = rating_dist.get(3, 0)

# Monthly trend
monthly_data = defaultdict(lambda: {'ratings': [], 'count': 0})
for r in reviews:
    date_str = r.get('date', '')
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            month_key = dt.strftime('%b %Y')
            monthly_data[month_key]['ratings'].append(r.get('rating', 0))
            monthly_data[month_key]['count'] += 1
        except:
            pass

# ============================================================================
# CREATE DASHBOARD
# ============================================================================

fig = plt.figure(figsize=(16, 12), facecolor='white')
fig.suptitle('HP APP - GOOGLE PLAY STORE EXECUTIVE SUMMARY\nOctober 2025 - January 2026 | Written Reviews Analysis',
             fontsize=14, fontweight='bold', y=0.98, color='#2c3e50')

# ============================================================================
# 1. TOP METRICS BAR
# ============================================================================

# Metric boxes at the top
metrics_config = [
    {"value": f"{total_reviews:,}", "label": "Total Reviews", "sublabel": "Google Play", "bg": "#e8f5e9", "border": "#4caf50"},
    {"value": f"{avg_rating:.2f}", "label": "Avg Rating", "sublabel": "out of 5.0", "bg": "#fff3e0", "border": "#ff9800"},
    {"value": f"{one_star_pct:.1f}%", "label": "1-Star Reviews", "sublabel": f"({one_star_count} reviews)", "bg": "#ffebee", "border": "#f44336"},
    {"value": f"{five_star_pct:.1f}%", "label": "5-Star Reviews", "sublabel": f"({five_star_count} reviews)", "bg": "#e3f2fd", "border": "#2196f3"},
    {"value": f"{negative_pct:.1f}%", "label": "Negative Sentiment", "sublabel": "(1-2 stars)", "bg": "#fce4ec", "border": "#e91e63"},
]

for i, m in enumerate(metrics_config):
    ax = fig.add_axes([0.05 + i * 0.185, 0.85, 0.16, 0.09])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Background box
    rect = FancyBboxPatch((0.05, 0.1), 0.9, 0.8, boxstyle="round,pad=0.02",
                          facecolor=m['bg'], edgecolor=m['border'], linewidth=2)
    ax.add_patch(rect)

    # Value
    ax.text(0.5, 0.6, m['value'], fontsize=20, fontweight='bold', ha='center', va='center', color='#2c3e50')
    # Label
    ax.text(0.5, 0.25, m['label'], fontsize=9, ha='center', va='center', color='#555')
    # Sublabel
    ax.text(0.5, 0.08, m['sublabel'], fontsize=7, ha='center', va='center', color='#888')

# ============================================================================
# 2. RATING DISTRIBUTION (Left)
# ============================================================================

ax_rating = fig.add_axes([0.05, 0.52, 0.28, 0.28])

stars = ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star']
counts = [rating_dist.get(5, 0), rating_dist.get(4, 0), rating_dist.get(3, 0),
          rating_dist.get(2, 0), rating_dist.get(1, 0)]
pcts = [c / total_reviews * 100 for c in counts]
colors = ['#4caf50', '#8bc34a', '#ffeb3b', '#ff9800', '#f44336']

bars = ax_rating.barh(stars, pcts, color=colors, edgecolor='white', height=0.6)

for bar, pct, count in zip(bars, pcts, counts):
    width = bar.get_width()
    ax_rating.text(width + 1, bar.get_y() + bar.get_height()/2,
                  f'{pct:.1f}% ({count})', va='center', fontsize=9)

ax_rating.set_xlabel('Percentage of Reviews (%)', fontsize=9)
ax_rating.set_title('Rating Distribution', fontweight='bold', fontsize=11, pad=10)
ax_rating.set_xlim(0, 75)
ax_rating.invert_yaxis()
ax_rating.spines['top'].set_visible(False)
ax_rating.spines['right'].set_visible(False)

# ============================================================================
# 3. SENTIMENT BREAKDOWN (Center)
# ============================================================================

ax_sentiment = fig.add_axes([0.38, 0.52, 0.25, 0.28])

sentiment_data = [negative_count, neutral_count, positive_count]
sentiment_labels = ['Negative', 'Neutral', 'Positive']
sentiment_colors = ['#f44336', '#ffeb3b', '#4caf50']

wedges, texts, autotexts = ax_sentiment.pie(
    sentiment_data,
    labels=None,
    colors=sentiment_colors,
    autopct='%1.1f%%',
    startangle=90,
    pctdistance=0.75,
    wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
)

for autotext in autotexts:
    autotext.set_fontsize(9)
    autotext.set_fontweight('bold')

# Center text
ax_sentiment.text(0, 0, f'{avg_rating:.1f}\nAvg', ha='center', va='center',
                  fontsize=14, fontweight='bold', color='#2c3e50')

ax_sentiment.set_title('Sentiment Breakdown', fontweight='bold', fontsize=11, pad=10)

# Legend below
ax_sentiment.legend(wedges, [f'{l} ({d})' for l, d in zip(sentiment_labels, sentiment_data)],
                    loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=8)

# ============================================================================
# 4. RATING COMPARISON BOX (Right)
# ============================================================================

ax_compare = fig.add_axes([0.68, 0.52, 0.27, 0.28])
ax_compare.axis('off')
ax_compare.set_xlim(0, 1)
ax_compare.set_ylim(0, 1)

ax_compare.text(0.5, 0.95, 'RATING COMPARISON', fontweight='bold', fontsize=10,
               ha='center', va='top', color='#2c3e50')

# Google Play Overall (from scrape info: 4.19)
rect1 = FancyBboxPatch((0.1, 0.65), 0.8, 0.22, boxstyle="round,pad=0.02",
                       facecolor='#e8f5e9', edgecolor='#4caf50', linewidth=1)
ax_compare.add_patch(rect1)
ax_compare.text(0.5, 0.8, '4.2', fontsize=18, fontweight='bold', ha='center', color='#4caf50')
ax_compare.text(0.5, 0.68, 'Play Store Overall (~34K ratings)', fontsize=8, ha='center', color='#666')

# Written Reviews
rect2 = FancyBboxPatch((0.1, 0.35), 0.8, 0.22, boxstyle="round,pad=0.02",
                       facecolor='#ffebee', edgecolor='#f44336', linewidth=1)
ax_compare.add_patch(rect2)
ax_compare.text(0.5, 0.5, f'{avg_rating:.2f}', fontsize=18, fontweight='bold', ha='center', color='#f44336')
ax_compare.text(0.5, 0.38, f'Oct+ Reviews ({total_reviews} reviews)', fontsize=8, ha='center', color='#666')

# Gap
gap = 4.2 - avg_rating
rect3 = FancyBboxPatch((0.1, 0.05), 0.8, 0.22, boxstyle="round,pad=0.02",
                       facecolor='#fff8e1', edgecolor='#ffc107', linewidth=1)
ax_compare.add_patch(rect3)
ax_compare.text(0.5, 0.2, f'-{gap:.2f}', fontsize=18, fontweight='bold', ha='center', color='#ff5722')
ax_compare.text(0.5, 0.08, 'Gap (Recent vs Overall)', fontsize=8, ha='center', color='#666')

# ============================================================================
# 5. TOP 5 CUSTOMER ISSUES
# ============================================================================

ax_issues = fig.add_axes([0.05, 0.18, 0.42, 0.28])

top_5 = issues_data['top_5_issues']
issue_names = [
    'Printing Problems',
    'Connectivity/WiFi Issues',
    'Scanning Issues',
    'Setup Difficulties',
    'App Crashes/Bugs'
]
issue_pcts = [i['percentage'] for i in top_5]
issue_colors = ['#f44336', '#ff5722', '#ff9800', '#ffc107', '#ffeb3b']

bars = ax_issues.barh(issue_names[::-1], issue_pcts[::-1], color=issue_colors[::-1],
                      edgecolor='white', height=0.6)

for bar, pct in zip(bars, issue_pcts[::-1]):
    width = bar.get_width()
    ax_issues.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                  f'{pct:.1f}%', va='center', fontsize=9, fontweight='bold')

ax_issues.set_xlabel('Percentage of Reviews Mentioning Issue', fontsize=9)
ax_issues.set_title('TOP 5 CUSTOMER ISSUES', fontweight='bold', fontsize=11,
                   pad=10, color='#c62828')
ax_issues.set_xlim(0, 35)
ax_issues.spines['top'].set_visible(False)
ax_issues.spines['right'].set_visible(False)

# ============================================================================
# 6. MONTHLY TREND
# ============================================================================

ax_trend = fig.add_axes([0.55, 0.18, 0.4, 0.28])

months_order = ['Oct 2025', 'Nov 2025', 'Dec 2025', 'Jan 2026']
monthly_avgs = []
monthly_counts = []

for m in months_order:
    if m in monthly_data:
        ratings_list = monthly_data[m]['ratings']
        monthly_avgs.append(sum(ratings_list) / len(ratings_list) if ratings_list else 0)
        monthly_counts.append(monthly_data[m]['count'])
    else:
        monthly_avgs.append(0)
        monthly_counts.append(0)

x = np.arange(len(months_order))
ax_trend.plot(x, monthly_avgs, 'o-', color='#f44336', linewidth=2, markersize=8, label='Avg Rating')
ax_trend.set_ylabel('Avg Rating', color='#f44336', fontsize=9)
ax_trend.tick_params(axis='y', labelcolor='#f44336')
ax_trend.set_ylim(1, 5)

# Add rating labels
for i, (xi, avg) in enumerate(zip(x, monthly_avgs)):
    ax_trend.annotate(f'{avg:.2f}', (xi, avg), textcoords="offset points",
                     xytext=(0, 10), ha='center', fontsize=9, color='#f44336')

ax2 = ax_trend.twinx()
ax2.bar(x, monthly_counts, alpha=0.3, color='#2196f3', width=0.4, label='# Reviews')
ax2.set_ylabel('Number of Reviews', color='#2196f3', fontsize=9)
ax2.tick_params(axis='y', labelcolor='#2196f3')

ax_trend.set_xticks(x)
ax_trend.set_xticklabels(['Oct 2025', 'Nov 2025', 'Dec 2025', 'Jan 2026'], fontsize=9)
ax_trend.set_title('Monthly Trend', fontweight='bold', fontsize=11, pad=10)
ax_trend.spines['top'].set_visible(False)

# Add count labels on bars
for i, count in enumerate(monthly_counts):
    ax2.text(i, count + 50, f'{count}', ha='center', fontsize=8, color='#2196f3')

# ============================================================================
# 7. KEY EXECUTIVE INSIGHTS
# ============================================================================

ax_insights = fig.add_axes([0.05, 0.01, 0.9, 0.12])
ax_insights.axis('off')

insights_box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                               facecolor='#fafafa', edgecolor='#ddd', linewidth=1,
                               transform=ax_insights.transAxes)
ax_insights.add_patch(insights_box)

insights_text = """KEY EXECUTIVE INSIGHTS

[RATING GAP]                                          [TOP ISSUES ANALYSIS]
• Play Store Overall: 4.2 stars (34K ratings)         #1 PRINTING PROBLEMS (26.1%): Core functionality failing
• Written Reviews: 2.39 stars (5,532 reviews)         #2 CONNECTIVITY (12.6%): WiFi/printer connection drops
• Users who write reviews are significantly           #3 SCANNING (8.6%): Scan/copy features broken or hidden
  more dissatisfied than silent raters                #4 SETUP (7.1%): Installation process too complicated
                                                      #5 APP CRASHES (6.8%): Stability and performance issues
[CRITICAL FINDINGS]
• 57.4% of all reviews are 1-star                     [RECOMMENDATIONS]
• December-January saw massive review surge           1. URGENT: Fix core printing functionality
• Negative sentiment (63.7%) exceeds positive         2. PRIORITY: Stabilize WiFi/network connectivity
• No developer responses to reviews (0%)              3. IMPROVE: Simplify setup and onboarding process
"""

ax_insights.text(0.02, 0.9, insights_text, transform=ax_insights.transAxes,
                fontsize=7.5, verticalalignment='top', fontfamily='monospace',
                color='#333')

# Save
plt.savefig('GooglePlay_HP_App_Oct_Executive_Summary.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Saved: GooglePlay_HP_App_Oct_Executive_Summary.png")

plt.close()
print("Done!")
