import matplotlib.pyplot as plt
import numpy as np

# --- DATA PREPARATION ---
# Top 5 Customer Issues
issues = ['Printing Problems', 'Connectivity/WiFi', 'App Crashes/Bugs', 'Scanning Issues', 'Setup/Installation']
issue_counts = [863, 332, 201, 171, 156]
issue_pct = [45.6, 17.5, 10.6, 9.0, 8.2]

# Monthly Trend (Oct '25 - Jan '26)
months = ['Oct 2025', 'Nov 2025', 'Dec 2025', 'Jan 2026']
reviews_vol = [637, 527, 427, 303]
avg_ratings = [1.98, 1.90, 2.14, 2.29]

# Rating Distribution
stars = ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars']
star_pct = [64.9, 8.1, 3.7, 4.1, 19.1]

# --- PLOTTING ---
fig = plt.figure(figsize=(18, 10))
fig.suptitle('HP App Executive Summary: Critical Issues & Trends (Oct 2025 - Jan 2026)', fontsize=20, weight='bold', y=0.98)

# 1. TOP CUSTOMER ISSUES (Horizontal Bar - The "Why")
ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
colors_issues = ['#d62728' if x == max(issue_counts) else '#A9A9A9' for x in issue_counts] # Red for top issue
bars = ax1.barh(issues, issue_pct, color=colors_issues)
ax1.set_title('Top Customer Pain Points (% of Negative Reviews)', fontsize=14, weight='bold', loc='left')
ax1.invert_yaxis() # Highest on top
ax1.set_xlabel('Percentage of Mentions')
ax1.grid(axis='x', linestyle='--', alpha=0.5)

# Add data labels
for bar, count, pct in zip(bars, issue_counts, issue_pct):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
             f'{pct}% ({count} reviews)', va='center', fontsize=11, weight='bold')

# 2. MONTHLY TREND (Combo Chart - The "Trend")
ax2 = plt.subplot2grid((2, 2), (1, 0))
ax2.set_title('Review Volume vs. Average Rating', fontsize=14, weight='bold', loc='left')

# Bar Chart for Volume
ax2_bar = ax2.bar(months, reviews_vol, color='#ADD8E6', label='Review Volume')
ax2.set_ylabel('Number of Reviews', color='#555')
ax2.tick_params(axis='y', labelcolor='#555')

# Line Chart for Rating (Dual Axis)
ax2_line = ax2.twinx()
ax2_line.plot(months, avg_ratings, color='#d62728', marker='o', linewidth=3, label='Avg Rating')
ax2_line.set_ylabel('Average Rating (1-5)', color='#d62728')
ax2_line.tick_params(axis='y', labelcolor='#d62728')
ax2_line.set_ylim(1, 5)

# Add labels for Rating
for i, txt in enumerate(avg_ratings):
    ax2_line.annotate(txt, (months[i], avg_ratings[i]), textcoords="offset points", xytext=(0,10), ha='center', color='#d62728', weight='bold')

# 3. RATING DISTRIBUTION (The "Reality")
ax3 = plt.subplot2grid((2, 2), (1, 1))
colors_stars = ['#d62728', '#FFA500', '#FFD700', '#9ACD32', '#228B22'] # Traffic light colors
ax3.bar(stars, star_pct, color=colors_stars)
ax3.set_title('Rating Distribution (1-Star Dominance)', fontsize=14, weight='bold', loc='left')
ax3.set_ylabel('Percentage of Reviews')
ax3.grid(axis='y', linestyle='--', alpha=0.3)

# Add labels
for i, v in enumerate(star_pct):
    ax3.text(i, v + 1, f'{v}%', ha='center', weight='bold')

plt.tight_layout(pad=3.0)
plt.savefig('HP_App_Executive_Summary_Chart.png', dpi=150, bbox_inches='tight', facecolor='white')
print("Saved: HP_App_Executive_Summary_Chart.png")
plt.close()
