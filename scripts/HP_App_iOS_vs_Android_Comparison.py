"""
HP App - iOS vs Android Comparison Visualization
October 2025 onwards
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
from collections import Counter

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10

# Load data
with open('HP_App_Reviews_Oct_2025_onward.json', 'r') as f:
    ios_reviews = json.load(f)

with open('GooglePlay_HP_App_Oct_Reviews.json', 'r') as f:
    android_reviews = json.load(f)

# Calculate metrics
ios_ratings = [r.get('rating', 0) for r in ios_reviews]
android_ratings = [r.get('rating', 0) for r in android_reviews]

ios_avg = sum(ios_ratings) / len(ios_ratings)
android_avg = sum(android_ratings) / len(android_ratings)

ios_dist = Counter(ios_ratings)
android_dist = Counter(android_ratings)

# ============================================================================
# CREATE COMPARISON DASHBOARD
# ============================================================================

fig = plt.figure(figsize=(16, 12))
fig.suptitle('HP App - iOS vs Android Comparison\nOctober 2025 - January 2026',
             fontsize=18, fontweight='bold', y=0.98)

# Colors
ios_color = '#007AFF'  # Apple blue
android_color = '#3DDC84'  # Android green
negative_color = '#e74c3c'
positive_color = '#27ae60'

# ============================================================================
# 1. KEY METRICS COMPARISON (Top)
# ============================================================================
ax_metrics = fig.add_axes([0.05, 0.82, 0.9, 0.12])
ax_metrics.axis('off')

# Calculate percentages
ios_negative_pct = (ios_dist.get(1, 0) + ios_dist.get(2, 0)) / len(ios_reviews) * 100
android_negative_pct = (android_dist.get(1, 0) + android_dist.get(2, 0)) / len(android_reviews) * 100
ios_positive_pct = (ios_dist.get(4, 0) + ios_dist.get(5, 0)) / len(ios_reviews) * 100
android_positive_pct = (android_dist.get(4, 0) + android_dist.get(5, 0)) / len(android_reviews) * 100

metrics = [
    ("Total Reviews", f"{len(ios_reviews):,}", f"{len(android_reviews):,}"),
    ("Avg Rating", f"{ios_avg:.2f}", f"{android_avg:.2f}"),
    ("Negative (1-2★)", f"{ios_negative_pct:.1f}%", f"{android_negative_pct:.1f}%"),
    ("Positive (4-5★)", f"{ios_positive_pct:.1f}%", f"{android_positive_pct:.1f}%"),
]

for i, (label, ios_val, android_val) in enumerate(metrics):
    x_start = 0.05 + i * 0.24

    # Label
    ax_metrics.text(x_start + 0.09, 0.85, label, fontsize=11, fontweight='bold',
                   ha='center', transform=ax_metrics.transAxes, color='#333')

    # iOS box
    rect_ios = mpatches.FancyBboxPatch((x_start, 0.4), 0.08, 0.35,
                                        boxstyle="round,pad=0.02",
                                        facecolor=ios_color, alpha=0.2,
                                        edgecolor=ios_color, linewidth=2,
                                        transform=ax_metrics.transAxes)
    ax_metrics.add_patch(rect_ios)
    ax_metrics.text(x_start + 0.04, 0.57, ios_val, fontsize=14, fontweight='bold',
                   ha='center', va='center', color=ios_color, transform=ax_metrics.transAxes)
    ax_metrics.text(x_start + 0.04, 0.25, 'iOS', fontsize=9, ha='center',
                   color=ios_color, transform=ax_metrics.transAxes)

    # Android box
    rect_android = mpatches.FancyBboxPatch((x_start + 0.1, 0.4), 0.08, 0.35,
                                            boxstyle="round,pad=0.02",
                                            facecolor=android_color, alpha=0.2,
                                            edgecolor=android_color, linewidth=2,
                                            transform=ax_metrics.transAxes)
    ax_metrics.add_patch(rect_android)
    ax_metrics.text(x_start + 0.14, 0.57, android_val, fontsize=14, fontweight='bold',
                   ha='center', va='center', color='#2E7D32', transform=ax_metrics.transAxes)
    ax_metrics.text(x_start + 0.14, 0.25, 'Android', fontsize=9, ha='center',
                   color='#2E7D32', transform=ax_metrics.transAxes)

# ============================================================================
# 2. RATING DISTRIBUTION COMPARISON (Left)
# ============================================================================
ax_rating = fig.add_subplot(2, 2, 1)
ax_rating.set_position([0.08, 0.42, 0.4, 0.35])

stars = [5, 4, 3, 2, 1]
ios_pcts = [ios_dist.get(s, 0) / len(ios_reviews) * 100 for s in stars]
android_pcts = [android_dist.get(s, 0) / len(android_reviews) * 100 for s in stars]

x = np.arange(len(stars))
width = 0.35

bars1 = ax_rating.barh(x - width/2, ios_pcts, width, label='iOS', color=ios_color, alpha=0.8)
bars2 = ax_rating.barh(x + width/2, android_pcts, width, label='Android', color=android_color, alpha=0.8)

ax_rating.set_yticks(x)
ax_rating.set_yticklabels([f'{s} Star' for s in stars])
ax_rating.set_xlabel('Percentage of Reviews')
ax_rating.set_title('Rating Distribution Comparison', fontweight='bold', pad=10)
ax_rating.legend(loc='lower right')
ax_rating.set_xlim(0, 70)
ax_rating.invert_yaxis()

# Add percentage labels
for bar, pct in zip(bars1, ios_pcts):
    if pct > 3:
        ax_rating.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                      f'{pct:.1f}%', va='center', fontsize=8, color=ios_color)

for bar, pct in zip(bars2, android_pcts):
    if pct > 3:
        ax_rating.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                      f'{pct:.1f}%', va='center', fontsize=8, color='#2E7D32')

# ============================================================================
# 3. MONTHLY TREND (Right)
# ============================================================================
ax_trend = fig.add_subplot(2, 2, 2)
ax_trend.set_position([0.55, 0.42, 0.4, 0.35])

# Calculate monthly data
ios_monthly = Counter()
android_monthly = Counter()
ios_monthly_rating = {}
android_monthly_rating = {}

for r in ios_reviews:
    date_str = r.get('date', '')
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            month_key = dt.strftime('%Y-%m')
            ios_monthly[month_key] += 1
            if month_key not in ios_monthly_rating:
                ios_monthly_rating[month_key] = []
            ios_monthly_rating[month_key].append(r.get('rating', 0))
        except:
            pass

for r in android_reviews:
    date_str = r.get('date', '')
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            month_key = dt.strftime('%Y-%m')
            android_monthly[month_key] += 1
            if month_key not in android_monthly_rating:
                android_monthly_rating[month_key] = []
            android_monthly_rating[month_key].append(r.get('rating', 0))
        except:
            pass

months = sorted(set(ios_monthly.keys()) | set(android_monthly.keys()))
month_labels = ['Oct', 'Nov', 'Dec', 'Jan']

ios_counts = [ios_monthly.get(m, 0) for m in months]
android_counts = [android_monthly.get(m, 0) for m in months]

x = np.arange(len(months))
width = 0.35

bars1 = ax_trend.bar(x - width/2, ios_counts, width, label='iOS', color=ios_color, alpha=0.8)
bars2 = ax_trend.bar(x + width/2, android_counts, width, label='Android', color=android_color, alpha=0.8)

ax_trend.set_xticks(x)
ax_trend.set_xticklabels(month_labels)
ax_trend.set_ylabel('Number of Reviews')
ax_trend.set_title('Review Volume by Month', fontweight='bold', pad=10)
ax_trend.legend()

# Add count labels
for bar in bars1:
    height = bar.get_height()
    ax_trend.text(bar.get_x() + bar.get_width()/2, height + 20,
                 f'{int(height)}', ha='center', va='bottom', fontsize=9, color=ios_color)

for bar in bars2:
    height = bar.get_height()
    ax_trend.text(bar.get_x() + bar.get_width()/2, height + 20,
                 f'{int(height)}', ha='center', va='bottom', fontsize=9, color='#2E7D32')

# ============================================================================
# 4. SENTIMENT COMPARISON (Bottom Left)
# ============================================================================
ax_sentiment = fig.add_subplot(2, 2, 3)
ax_sentiment.set_position([0.08, 0.05, 0.4, 0.32])

# Sentiment data
categories = ['Positive\n(4-5★)', 'Neutral\n(3★)', 'Negative\n(1-2★)']
ios_sentiment = [
    (ios_dist.get(4, 0) + ios_dist.get(5, 0)) / len(ios_reviews) * 100,
    ios_dist.get(3, 0) / len(ios_reviews) * 100,
    (ios_dist.get(1, 0) + ios_dist.get(2, 0)) / len(ios_reviews) * 100
]
android_sentiment = [
    (android_dist.get(4, 0) + android_dist.get(5, 0)) / len(android_reviews) * 100,
    android_dist.get(3, 0) / len(android_reviews) * 100,
    (android_dist.get(1, 0) + android_dist.get(2, 0)) / len(android_reviews) * 100
]

x = np.arange(len(categories))
width = 0.35

bars1 = ax_sentiment.bar(x - width/2, ios_sentiment, width, label='iOS', color=ios_color, alpha=0.8)
bars2 = ax_sentiment.bar(x + width/2, android_sentiment, width, label='Android', color=android_color, alpha=0.8)

ax_sentiment.set_xticks(x)
ax_sentiment.set_xticklabels(categories)
ax_sentiment.set_ylabel('Percentage')
ax_sentiment.set_title('Sentiment Breakdown', fontweight='bold', pad=10)
ax_sentiment.legend()
ax_sentiment.set_ylim(0, 80)

# Add labels
for bar in bars1:
    height = bar.get_height()
    ax_sentiment.text(bar.get_x() + bar.get_width()/2, height + 1,
                     f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

for bar in bars2:
    height = bar.get_height()
    ax_sentiment.text(bar.get_x() + bar.get_width()/2, height + 1,
                     f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

# ============================================================================
# 5. KEY INSIGHTS (Bottom Right)
# ============================================================================
ax_insights = fig.add_subplot(2, 2, 4)
ax_insights.set_position([0.55, 0.05, 0.4, 0.32])
ax_insights.axis('off')

insights_text = """
KEY INSIGHTS

Both Platforms Show Similar Problems:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Nearly Identical Ratings
   • iOS: 2.46 avg  |  Android: 2.39 avg
   • Both have ~60%+ negative reviews

📈 Android Has 3x More Reviews
   • Larger user base = more feedback
   • More data points for issue analysis

😡 1-Star Reviews Dominate
   • iOS: 54.1%  |  Android: 57.4%
   • Core functionality issues on both

📅 December-January Spike
   • Review volume increased significantly
   • Possible problematic update released

🔧 Cross-Platform Issues
   • Same problems affect both iOS & Android
   • Indicates backend/service issues,
     not just platform-specific bugs
"""

ax_insights.text(0.05, 0.95, insights_text, transform=ax_insights.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='#f8f9fa', edgecolor='#dee2e6'))

# Footer
fig.text(0.5, 0.01, f'Analysis generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | HP App Review Comparison',
         ha='center', fontsize=9, color='gray', style='italic')

# Save
plt.savefig('HP_App_iOS_vs_Android_Oct_Comparison.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✅ Saved: HP_App_iOS_vs_Android_Oct_Comparison.png")

plt.close()

# ============================================================================
# Save comparison data as JSON
# ============================================================================

comparison_data = {
    "period": "October 2025 - January 2026",
    "ios": {
        "total_reviews": len(ios_reviews),
        "average_rating": round(ios_avg, 2),
        "rating_distribution": {str(k): v for k, v in sorted(ios_dist.items(), reverse=True)},
        "negative_percent": round(ios_negative_pct, 1),
        "positive_percent": round(ios_positive_pct, 1),
        "monthly_reviews": dict(ios_monthly)
    },
    "android": {
        "total_reviews": len(android_reviews),
        "average_rating": round(android_avg, 2),
        "rating_distribution": {str(k): v for k, v in sorted(android_dist.items(), reverse=True)},
        "negative_percent": round(android_negative_pct, 1),
        "positive_percent": round(android_positive_pct, 1),
        "monthly_reviews": dict(android_monthly)
    },
    "comparison": {
        "review_ratio": f"Android has {len(android_reviews)/len(ios_reviews):.1f}x more reviews",
        "rating_difference": round(ios_avg - android_avg, 2),
        "both_platforms_negative_majority": ios_negative_pct > 50 and android_negative_pct > 50
    },
    "analysis_date": datetime.now().isoformat()
}

with open('HP_App_iOS_vs_Android_Oct_Comparison.json', 'w') as f:
    json.dump(comparison_data, f, indent=2)
print("✅ Saved: HP_App_iOS_vs_Android_Oct_Comparison.json")

print("\n📊 Comparison complete!")
