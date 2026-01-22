"""
HP App Store Reviews - Visualization Dashboard
Generates charts comparing Last 30 Days vs Overall data
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# DATA
# ============================================================================

# Last 30 Days Data
data_30_days = {
    "total_reviews": 658,
    "average_rating": 2.60,
    "rating_distribution": {5: 222, 4: 17, 3: 37, 2: 43, 1: 339},
    "country_distribution": {
        "US": 351, "GB": 62, "DE": 39, "CA": 35, "FR": 35,
        "IT": 25, "MX": 24, "BR": 18, "AU": 17, "ES": 17
    },
    "pain_points": {
        "WiFi/Connectivity": 15,
        "Scan/Fax Issues": 13,
        "Setup Problems": 12,
        "Subscription Model": 5,
        "Account Required": 5,
        "App Performance": 5
    }
}

# Overall Data
data_overall = {
    "total_reviews": 6275,
    "average_rating": 2.83,
    "rating_distribution": {5: 2332, 4: 336, 3: 378, 2: 417, 1: 2812},
    "country_distribution": {
        "US": 500, "GB": 500, "CA": 500, "AU": 500, "IN": 500,
        "DE": 500, "BR": 500, "MX": 500, "ES": 500, "NL": 500
    },
    "pain_points": {
        "WiFi/Connectivity": 30,
        "Subscription Model": 25,
        "Setup Problems": 18,
        "Slow Performance": 15,
        "Printer Offline": 20,
        "Account Required": 10
    }
}

# Colors
COLORS = {
    'negative': '#E74C3C',
    'positive': '#27AE60',
    'neutral': '#95A5A6',
    'primary': '#3498DB',
    'secondary': '#9B59B6',
    'warning': '#F39C12',
    'dark': '#2C3E50',
    'star_colors': ['#E74C3C', '#E67E22', '#F1C40F', '#2ECC71', '#27AE60']
}

# ============================================================================
# CHART 1: Rating Distribution Comparison
# ============================================================================

def create_rating_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ratings = [1, 2, 3, 4, 5]
    colors = COLORS['star_colors']

    # Last 30 Days
    ax1 = axes[0]
    counts_30 = [data_30_days["rating_distribution"][r] for r in ratings]
    total_30 = sum(counts_30)
    percentages_30 = [c/total_30*100 for c in counts_30]

    bars1 = ax1.barh(ratings, percentages_30, color=colors, height=0.7, edgecolor='white', linewidth=1)
    ax1.set_xlabel('Percentage of Reviews (%)', fontweight='bold')
    ax1.set_ylabel('Star Rating', fontweight='bold')
    ax1.set_title(f'Last 30 Days\n(n={total_30}, Avg: {data_30_days["average_rating"]:.2f})', fontsize=12)
    ax1.set_xlim(0, 60)
    ax1.set_yticks(ratings)
    ax1.set_yticklabels(['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'])

    for bar, pct, count in zip(bars1, percentages_30, counts_30):
        ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{pct:.1f}% ({count})', va='center', fontsize=9)

    # Overall
    ax2 = axes[1]
    counts_all = [data_overall["rating_distribution"][r] for r in ratings]
    total_all = sum(counts_all)
    percentages_all = [c/total_all*100 for c in counts_all]

    bars2 = ax2.barh(ratings, percentages_all, color=colors, height=0.7, edgecolor='white', linewidth=1)
    ax2.set_xlabel('Percentage of Reviews (%)', fontweight='bold')
    ax2.set_title(f'Overall (All Time)\n(n={total_all}, Avg: {data_overall["average_rating"]:.2f})', fontsize=12)
    ax2.set_xlim(0, 60)
    ax2.set_yticks(ratings)
    ax2.set_yticklabels(['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'])

    for bar, pct, count in zip(bars2, percentages_all, counts_all):
        ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{pct:.1f}% ({count})', va='center', fontsize=9)

    fig.suptitle('HP App - Rating Distribution Comparison', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, 'HP_viz_rating_comparison.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath

# ============================================================================
# CHART 2: Sentiment Donut Charts
# ============================================================================

def create_sentiment_donuts():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Last 30 Days sentiment
    ax1 = axes[0]
    # Calculate sentiment from ratings (1-2 = negative, 3 = neutral, 4-5 = positive)
    neg_30 = data_30_days["rating_distribution"][1] + data_30_days["rating_distribution"][2]
    neu_30 = data_30_days["rating_distribution"][3]
    pos_30 = data_30_days["rating_distribution"][4] + data_30_days["rating_distribution"][5]
    total_30 = neg_30 + neu_30 + pos_30

    sizes_30 = [neg_30, neu_30, pos_30]
    labels_30 = [f'Negative\n{neg_30/total_30*100:.1f}%',
                 f'Neutral\n{neu_30/total_30*100:.1f}%',
                 f'Positive\n{pos_30/total_30*100:.1f}%']
    colors_sent = [COLORS['negative'], COLORS['neutral'], COLORS['positive']]

    wedges1, texts1 = ax1.pie(sizes_30, colors=colors_sent, startangle=90,
                               wedgeprops=dict(width=0.5, edgecolor='white'))
    ax1.set_title(f'Last 30 Days\n(n={total_30})', fontsize=12, fontweight='bold')

    # Add center text
    ax1.text(0, 0, f'{data_30_days["average_rating"]:.1f}\nAvg', ha='center', va='center',
             fontsize=20, fontweight='bold', color=COLORS['dark'])

    # Overall sentiment
    ax2 = axes[1]
    neg_all = data_overall["rating_distribution"][1] + data_overall["rating_distribution"][2]
    neu_all = data_overall["rating_distribution"][3]
    pos_all = data_overall["rating_distribution"][4] + data_overall["rating_distribution"][5]
    total_all = neg_all + neu_all + pos_all

    sizes_all = [neg_all, neu_all, pos_all]

    wedges2, texts2 = ax2.pie(sizes_all, colors=colors_sent, startangle=90,
                               wedgeprops=dict(width=0.5, edgecolor='white'))
    ax2.set_title(f'Overall (All Time)\n(n={total_all})', fontsize=12, fontweight='bold')
    ax2.text(0, 0, f'{data_overall["average_rating"]:.1f}\nAvg', ha='center', va='center',
             fontsize=20, fontweight='bold', color=COLORS['dark'])

    # Legend
    legend_elements = [mpatches.Patch(facecolor=COLORS['negative'], label='Negative (1-2 stars)'),
                       mpatches.Patch(facecolor=COLORS['neutral'], label='Neutral (3 stars)'),
                       mpatches.Patch(facecolor=COLORS['positive'], label='Positive (4-5 stars)')]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.05))

    fig.suptitle('HP App - Sentiment Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, 'HP_viz_sentiment.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath

# ============================================================================
# CHART 3: Pain Points - Last 30 Days
# ============================================================================

def create_pain_points_chart():
    fig, ax = plt.subplots(figsize=(12, 7))

    pain_points = data_30_days["pain_points"]
    issues = list(pain_points.keys())
    percentages = list(pain_points.values())

    # Sort by percentage
    sorted_data = sorted(zip(issues, percentages), key=lambda x: x[1], reverse=True)
    issues = [x[0] for x in sorted_data]
    percentages = [x[1] for x in sorted_data]

    # Color gradient based on severity
    colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(issues)))[::-1]

    y_pos = np.arange(len(issues))
    bars = ax.barh(y_pos, percentages, color=colors, height=0.6, edgecolor='white', linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(issues, fontsize=11)
    ax.set_xlabel('Percentage of Reviews Mentioning Issue (%)', fontweight='bold')
    ax.set_title('HP App - Top Customer Pain Points\n(Last 30 Days Analysis)',
                 fontsize=14, fontweight='bold')
    ax.set_xlim(0, 20)

    # Add value labels
    for bar, pct in zip(bars, percentages):
        width = bar.get_width()
        ax.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                f'{pct}%', va='center', fontsize=10, fontweight='bold')

    # Add severity indicators
    severity_colors = {'CRITICAL': '#E74C3C', 'HIGH': '#F39C12', 'MEDIUM': '#3498DB'}
    severity_map = {
        'WiFi/Connectivity': 'CRITICAL',
        'Scan/Fax Issues': 'HIGH',
        'Setup Problems': 'CRITICAL',
        'Subscription Model': 'CRITICAL',
        'Account Required': 'HIGH',
        'App Performance': 'MEDIUM'
    }

    for i, issue in enumerate(issues):
        severity = severity_map.get(issue, 'MEDIUM')
        ax.text(-0.5, i, severity, va='center', ha='right', fontsize=8,
                color=severity_colors[severity], fontweight='bold')

    ax.invert_yaxis()
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, 'HP_viz_pain_points_30.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath

# ============================================================================
# CHART 4: Country Distribution
# ============================================================================

def create_country_chart():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Last 30 Days
    ax1 = axes[0]
    countries_30 = list(data_30_days["country_distribution"].keys())[:8]
    values_30 = list(data_30_days["country_distribution"].values())[:8]

    colors_30 = plt.cm.Blues(np.linspace(0.4, 0.9, len(countries_30)))
    bars1 = ax1.bar(countries_30, values_30, color=colors_30, edgecolor='white', linewidth=1)
    ax1.set_xlabel('Country', fontweight='bold')
    ax1.set_ylabel('Number of Reviews', fontweight='bold')
    ax1.set_title(f'Last 30 Days\n(Total: {data_30_days["total_reviews"]})', fontsize=12)

    for bar, val in zip(bars1, values_30):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                str(val), ha='center', fontsize=9, fontweight='bold')

    # Overall
    ax2 = axes[1]
    countries_all = list(data_overall["country_distribution"].keys())[:8]
    values_all = list(data_overall["country_distribution"].values())[:8]

    colors_all = plt.cm.Greens(np.linspace(0.4, 0.9, len(countries_all)))
    bars2 = ax2.bar(countries_all, values_all, color=colors_all, edgecolor='white', linewidth=1)
    ax2.set_xlabel('Country', fontweight='bold')
    ax2.set_title(f'Overall (All Time)\n(Total: {data_overall["total_reviews"]})', fontsize=12)

    for bar, val in zip(bars2, values_all):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                str(val), ha='center', fontsize=9, fontweight='bold')

    fig.suptitle('HP App - Reviews by Country', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, 'HP_viz_countries.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath

# ============================================================================
# CHART 5: Executive Dashboard
# ============================================================================

def create_executive_dashboard():
    fig = plt.figure(figsize=(16, 12))

    # Title
    fig.suptitle('HP App - Executive Dashboard\nCustomer Intelligence Report',
                 fontsize=18, fontweight='bold', y=0.98)

    # Grid layout
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)

    # ---- Key Metrics Cards (Top Row) ----
    ax_metrics = fig.add_subplot(gs[0, :])
    ax_metrics.axis('off')

    metrics = [
        ('Last 30 Days', f'{data_30_days["total_reviews"]}', 'Reviews', COLORS['primary']),
        ('Avg Rating (30d)', f'{data_30_days["average_rating"]:.2f}', '/ 5.0', COLORS['warning']),
        ('1-Star Rate (30d)', '51.5%', 'of reviews', COLORS['negative']),
        ('Overall Reviews', f'{data_overall["total_reviews"]:,}', 'Total', COLORS['secondary']),
        ('Avg Rating (All)', f'{data_overall["average_rating"]:.2f}', '/ 5.0', COLORS['positive']),
    ]

    for i, (label, value, sub, color) in enumerate(metrics):
        x = 0.1 + i * 0.18
        ax_metrics.add_patch(plt.Rectangle((x, 0.1), 0.15, 0.8, facecolor=color, alpha=0.1,
                                           edgecolor=color, linewidth=2, transform=ax_metrics.transAxes))
        ax_metrics.text(x + 0.075, 0.7, value, ha='center', va='center', fontsize=24,
                        fontweight='bold', color=color, transform=ax_metrics.transAxes)
        ax_metrics.text(x + 0.075, 0.4, sub, ha='center', va='center', fontsize=10,
                        color=COLORS['dark'], transform=ax_metrics.transAxes)
        ax_metrics.text(x + 0.075, 0.2, label, ha='center', va='center', fontsize=9,
                        fontweight='bold', color=COLORS['dark'], transform=ax_metrics.transAxes)

    # ---- Rating Comparison (Middle Left) ----
    ax_rating = fig.add_subplot(gs[1, 0])

    ratings = ['1 Star', '2 Star', '3 Star', '4 Star', '5 Star']
    x = np.arange(len(ratings))
    width = 0.35

    pct_30 = [data_30_days["rating_distribution"][i]/data_30_days["total_reviews"]*100 for i in [1,2,3,4,5]]
    pct_all = [data_overall["rating_distribution"][i]/data_overall["total_reviews"]*100 for i in [1,2,3,4,5]]

    ax_rating.bar(x - width/2, pct_30, width, label='Last 30 Days', color=COLORS['primary'], alpha=0.8)
    ax_rating.bar(x + width/2, pct_all, width, label='Overall', color=COLORS['secondary'], alpha=0.8)
    ax_rating.set_ylabel('% of Reviews')
    ax_rating.set_title('Rating Distribution', fontweight='bold')
    ax_rating.set_xticks(x)
    ax_rating.set_xticklabels(ratings, fontsize=8)
    ax_rating.legend(fontsize=8)
    ax_rating.set_ylim(0, 60)

    # ---- Sentiment Pie (Middle Center) ----
    ax_sent = fig.add_subplot(gs[1, 1])

    neg_30 = data_30_days["rating_distribution"][1] + data_30_days["rating_distribution"][2]
    neu_30 = data_30_days["rating_distribution"][3]
    pos_30 = data_30_days["rating_distribution"][4] + data_30_days["rating_distribution"][5]

    sizes = [neg_30, neu_30, pos_30]
    colors_sent = [COLORS['negative'], COLORS['neutral'], COLORS['positive']]
    labels = ['Negative', 'Neutral', 'Positive']

    wedges, texts, autotexts = ax_sent.pie(sizes, colors=colors_sent, autopct='%1.1f%%',
                                            startangle=90, pctdistance=0.75)
    ax_sent.set_title('Sentiment (Last 30 Days)', fontweight='bold')
    ax_sent.legend(labels, loc='lower center', fontsize=8, ncol=3, bbox_to_anchor=(0.5, -0.1))

    # ---- Top Pain Points (Middle Right) ----
    ax_pain = fig.add_subplot(gs[1, 2])

    issues = list(data_30_days["pain_points"].keys())[:5]
    pcts = list(data_30_days["pain_points"].values())[:5]

    y_pos = np.arange(len(issues))
    colors_pain = plt.cm.Reds(np.linspace(0.4, 0.8, len(issues)))

    ax_pain.barh(y_pos, pcts, color=colors_pain, height=0.6)
    ax_pain.set_yticks(y_pos)
    ax_pain.set_yticklabels(issues, fontsize=8)
    ax_pain.set_xlabel('% of Reviews')
    ax_pain.set_title('Top Pain Points (30d)', fontweight='bold')
    ax_pain.invert_yaxis()

    for i, pct in enumerate(pcts):
        ax_pain.text(pct + 0.3, i, f'{pct}%', va='center', fontsize=8)

    # ---- Countries (Bottom Left) ----
    ax_country = fig.add_subplot(gs[2, 0])

    countries = list(data_30_days["country_distribution"].keys())[:6]
    values = list(data_30_days["country_distribution"].values())[:6]

    colors_country = plt.cm.Blues(np.linspace(0.4, 0.9, len(countries)))
    ax_country.bar(countries, values, color=colors_country)
    ax_country.set_title('Reviews by Country (30d)', fontweight='bold')
    ax_country.set_ylabel('Count')

    # ---- Trend Insight (Bottom Center & Right) ----
    ax_insight = fig.add_subplot(gs[2, 1:])
    ax_insight.axis('off')

    insight_text = """
    KEY INSIGHTS FOR LEADERSHIP

    1. CRITICAL: 51.5% of reviews in last 30 days are 1-star (up from 45% overall)

    2. TOP PRIORITY: WiFi/Connectivity issues affect 15% of all reviewers
       - Users report daily reboots required
       - "Never HP again" sentiment growing

    3. SUBSCRIPTION BACKLASH: Only 5% mention it, but 95% negative
       - Creates "trapped customer" perception
       - Highest brand damage per complaint

    4. QUICK WINS AVAILABLE:
       - Fix mobile fax access (recently broken)
       - Add quick-reconnect button
       - Make account optional

    TARGET: Move from 2.6 to 3.5+ rating in 90 days
    """

    ax_insight.text(0.05, 0.95, insight_text, transform=ax_insight.transAxes,
                    fontsize=10, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='#f8f9fa', edgecolor='#dee2e6'))

    filepath = os.path.join(OUTPUT_DIR, 'HP_viz_executive_dashboard.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath

# ============================================================================
# CHART 6: 30-Day vs Overall Comparison Summary
# ============================================================================

def create_comparison_summary():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    # Title
    ax.text(0.5, 0.95, 'HP App - 30 Days vs Overall Comparison',
            ha='center', va='top', fontsize=18, fontweight='bold', transform=ax.transAxes)

    # Create comparison table
    metrics = [
        ('Total Reviews', f'{data_30_days["total_reviews"]:,}', f'{data_overall["total_reviews"]:,}', ''),
        ('Average Rating', f'{data_30_days["average_rating"]:.2f}', f'{data_overall["average_rating"]:.2f}',
         'WORSE' if data_30_days["average_rating"] < data_overall["average_rating"] else 'BETTER'),
        ('1-Star %', '51.5%', '44.8%', 'WORSE'),
        ('5-Star %', '33.7%', '37.2%', 'WORSE'),
        ('Negative Sentiment', '58%', '51%', 'WORSE'),
        ('Positive Sentiment', '36%', '43%', 'WORSE'),
    ]

    # Table header
    headers = ['Metric', 'Last 30 Days', 'Overall', 'Trend']
    col_widths = [0.3, 0.2, 0.2, 0.15]
    col_positions = [0.1, 0.4, 0.6, 0.8]

    y_start = 0.82
    row_height = 0.08

    # Header row
    for i, (header, pos) in enumerate(zip(headers, col_positions)):
        ax.text(pos, y_start, header, ha='center', va='center', fontsize=12,
                fontweight='bold', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor=COLORS['primary'], edgecolor='none', alpha=0.8))
        ax.text(pos, y_start, header, ha='center', va='center', fontsize=12,
                fontweight='bold', color='white', transform=ax.transAxes)

    # Data rows
    for row_idx, (metric, val_30, val_all, trend) in enumerate(metrics):
        y = y_start - (row_idx + 1) * row_height

        # Alternating row colors
        if row_idx % 2 == 0:
            ax.add_patch(plt.Rectangle((0.05, y - row_height/2), 0.9, row_height,
                                       facecolor='#f8f9fa', edgecolor='none', transform=ax.transAxes))

        ax.text(col_positions[0], y, metric, ha='center', va='center', fontsize=11, transform=ax.transAxes)
        ax.text(col_positions[1], y, val_30, ha='center', va='center', fontsize=11,
                fontweight='bold', color=COLORS['primary'], transform=ax.transAxes)
        ax.text(col_positions[2], y, val_all, ha='center', va='center', fontsize=11,
                fontweight='bold', color=COLORS['secondary'], transform=ax.transAxes)

        trend_color = COLORS['negative'] if trend == 'WORSE' else COLORS['positive'] if trend == 'BETTER' else COLORS['neutral']
        ax.text(col_positions[3], y, trend, ha='center', va='center', fontsize=10,
                fontweight='bold', color=trend_color, transform=ax.transAxes)

    # Bottom insight box
    insight = """
    KEY TAKEAWAY: The last 30 days show DETERIORATING metrics across the board.

    - 1-star reviews UP from 45% to 51.5%
    - Average rating DOWN from 2.83 to 2.60
    - Negative sentiment UP from 51% to 58%

    URGENT ACTION REQUIRED to reverse this trend.
    """

    ax.text(0.5, 0.15, insight, ha='center', va='center', fontsize=11, transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='#fff3cd', edgecolor='#ffc107', linewidth=2))

    filepath = os.path.join(OUTPUT_DIR, 'HP_viz_comparison_summary.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {filepath}")
    return filepath

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("HP SMART APP - VISUALIZATION GENERATOR")
    print("="*60 + "\n")

    print("Generating visualizations...\n")

    charts = [
        ("Rating Distribution Comparison", create_rating_comparison),
        ("Sentiment Analysis", create_sentiment_donuts),
        ("Pain Points (30 Days)", create_pain_points_chart),
        ("Country Distribution", create_country_chart),
        ("Executive Dashboard", create_executive_dashboard),
        ("30 Days vs Overall Comparison", create_comparison_summary),
    ]

    generated = []
    for name, func in charts:
        print(f"Creating: {name}...")
        try:
            filepath = func()
            generated.append(filepath)
        except Exception as e:
            print(f"  Error: {e}")

    print("\n" + "="*60)
    print(f"COMPLETE - Generated {len(generated)} visualizations")
    print("="*60)
    print("\nFiles saved:")
    for f in generated:
        print(f"  - {os.path.basename(f)}")
    print()

if __name__ == "__main__":
    main()
