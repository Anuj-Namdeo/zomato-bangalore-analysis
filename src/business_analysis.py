"""
business_analysis.py — 25 High-Value Business Questions for Zomato Bangalore
Author: Your Name

Each function:
  - Answers ONE business question
  - Returns a results DataFrame
  - Prints a formatted insight
  - Saves a visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import (
    get_logger, Cols, save_figure, set_plot_style, ZOMATO_PALETTE, ZOMATO_RED
)

logger = get_logger("business_analysis")
set_plot_style()


def _print_question(n: int, question: str):
    print(f"\n{'─'*60}\n❓ Q{n}: {question}\n{'─'*60}")


# ─────────────────────────────────────────────
# Q1: Which areas have the highest restaurant density?
# ─────────────────────────────────────────────
def q1_restaurant_density_by_location(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(1, "Which areas have the highest restaurant density in Bangalore?")
    result = (
        df.groupby(Cols.LOCATION)
        .agg(
            restaurant_count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
        )
        .sort_values("restaurant_count", ascending=False)
        .round(2)
        .reset_index()
    )
    result["market_share_pct"] = (result["restaurant_count"] / result["restaurant_count"].sum() * 100).round(2)

    top5 = result.head(5)
    print(f"✅ Top 5 Areas:\n{top5[['location','restaurant_count','avg_rating','avg_cost','market_share_pct']].to_string(index=False)}")
    print(f"\n💡 RECOMMENDATION: Koramangala and BTM hold the largest market share. New entrants should target underserved high-growth areas.")

    fig, ax = plt.subplots(figsize=(14, 6))
    top20 = result.head(20)
    bars = ax.bar(top20[Cols.LOCATION], top20["restaurant_count"], color=ZOMATO_RED, alpha=0.85)
    ax.set_title("Top 20 Locations by Restaurant Count", fontweight="bold")
    ax.set_ylabel("Number of Restaurants")
    plt.xticks(rotation=45, ha="right")
    ax.bar_label(bars, padding=2, fontsize=8)
    plt.tight_layout()
    save_figure(fig, "q1_restaurant_density.png", "business")
    return result


# ─────────────────────────────────────────────
# Q2: Does online ordering correlate with higher ratings?
# ─────────────────────────────────────────────
def q2_online_order_impact_on_rating(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(2, "Does accepting online orders correlate with higher ratings?")
    df_q = df[[Cols.ONLINE_ORDER, Cols.RATE_NUMERIC]].dropna()
    online = df_q[df_q[Cols.ONLINE_ORDER] == True][Cols.RATE_NUMERIC]
    offline = df_q[df_q[Cols.ONLINE_ORDER] == False][Cols.RATE_NUMERIC]

    t_stat, p_val = stats.ttest_ind(online, offline)
    result = pd.DataFrame({
        "group": ["Online Order", "No Online Order"],
        "count": [len(online), len(offline)],
        "mean_rating": [online.mean(), offline.mean()],
        "median_rating": [online.median(), offline.median()],
        "std_rating": [online.std(), offline.std()],
    }).round(3)

    print(result.to_string(index=False))
    print(f"\n📊 Independent T-Test: t={t_stat:.3f}, p={p_val:.6f}")
    sig = "SIGNIFICANT" if p_val < 0.05 else "NOT SIGNIFICANT"
    print(f"💡 INSIGHT: Difference is statistically {sig} (α=0.05)")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(result["group"], result["mean_rating"],
           color=[ZOMATO_RED, "#2D9CDB"], alpha=0.85, edgecolor="white", width=0.5)
    ax.set_ylim(3.0, 4.5)
    ax.set_ylabel("Mean Rating")
    ax.set_title("Mean Rating: Online Order vs No Online Order", fontweight="bold")
    for i, (val, grp) in enumerate(zip(result["mean_rating"], result["group"])):
        ax.text(i, val + 0.02, f"{val:.3f}", ha="center", fontsize=11, fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "q2_online_order_rating.png", "business")
    return result


# ─────────────────────────────────────────────
# Q3: What is the price-rating sweet spot?
# ─────────────────────────────────────────────
def q3_price_rating_sweet_spot(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(3, "What is the price-rating sweet spot for Bangalore restaurants?")
    result = (
        df.groupby(Cols.COST_BUCKET, observed=True)
        .agg(
            count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            median_rating=(Cols.RATE_NUMERIC, "median"),
            avg_votes=(Cols.VOTES, "mean"),
        )
        .round(3)
        .reset_index()
    )
    best = result.loc[result["avg_rating"].idxmax(), Cols.COST_BUCKET]
    print(result.to_string(index=False))
    print(f"\n💡 Sweet spot: '{best}' segment has the highest average rating.")
    print(f"💡 RECOMMENDATION: Budget and mid-range segments are most price-competitive; quality differentiation is key.")

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    x = range(len(result))
    bars = ax1.bar(x, result["count"], color="#FFB829", alpha=0.7, label="Restaurant Count")
    ax2.plot(x, result["avg_rating"], "o-", color=ZOMATO_RED, linewidth=2.5, markersize=8, label="Avg Rating")
    ax1.set_xticks(x)
    ax1.set_xticklabels(result[Cols.COST_BUCKET].astype(str), rotation=20, ha="right")
    ax1.set_ylabel("Restaurant Count", color="#FFB829")
    ax2.set_ylabel("Average Rating", color=ZOMATO_RED)
    ax1.set_title("Price Segment vs Rating (Count + Rating overlay)", fontweight="bold")
    ax1.legend(loc="upper left"); ax2.legend(loc="upper right")
    plt.tight_layout()
    save_figure(fig, "q3_price_rating_sweet_spot.png", "business")
    return result


# ─────────────────────────────────────────────
# Q4: Which cuisines command premium pricing?
# ─────────────────────────────────────────────
def q4_cuisine_premium_pricing(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(4, "Which cuisines command premium pricing in Bangalore?")
    result = (
        df.groupby(Cols.PRIMARY_CUISINE)
        .agg(
            count=(Cols.NAME, "count"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
        )
        .query("count >= 30")
        .sort_values("avg_cost", ascending=False)
        .round(2)
        .reset_index()
    )
    print(result.head(10).to_string(index=False))
    print(f"\n💡 Most expensive cuisine: {result.iloc[0][Cols.PRIMARY_CUISINE]} @ avg ₹{result.iloc[0]['avg_cost']:.0f} for two")

    top10 = result.head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("YlOrRd", len(top10))[::-1]
    bars = ax.barh(top10[Cols.PRIMARY_CUISINE][::-1], top10["avg_cost"][::-1], color=colors)
    ax.bar_label(bars, fmt="₹%.0f", padding=3)
    ax.set_xlabel("Average Cost for Two (₹)")
    ax.set_title("Top 10 Premium Cuisines by Avg Cost", fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "q4_cuisine_premium.png", "business")
    return result


# ─────────────────────────────────────────────
# Q5: Table booking impact on rating and votes
# ─────────────────────────────────────────────
def q5_table_booking_impact(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(5, "Does offering table booking improve ratings and engagement?")
    result = (
        df.groupby(Cols.BOOK_TABLE)
        .agg(
            count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            avg_votes=(Cols.VOTES, "mean"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
        )
        .round(3)
        .reset_index()
    )
    result[Cols.BOOK_TABLE] = result[Cols.BOOK_TABLE].map({True: "Yes", False: "No"})
    print(result.to_string(index=False))
    print("\n💡 Restaurants offering table booking tend to be upscale with higher ratings — correlation with premium positioning.")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    metrics = ["avg_rating", "avg_votes", "avg_cost"]
    titles = ["Avg Rating", "Avg Votes", "Avg Cost (₹)"]
    for ax, metric, title in zip(axes, metrics, titles):
        ax.bar(result[Cols.BOOK_TABLE], result[metric],
               color=[ZOMATO_RED, "#2D9CDB"], alpha=0.85, width=0.5)
        ax.set_title(title, fontweight="bold")
        ax.set_ylabel(title)
        for i, val in enumerate(result[metric]):
            ax.text(i, val * 0.98, f"{val:.2f}", ha="center", fontsize=11, va="top", color="white", fontweight="bold")
    fig.suptitle("Table Booking: Impact on Key Metrics", fontweight="bold", fontsize=14)
    plt.tight_layout()
    save_figure(fig, "q5_table_booking.png", "business")
    return result


# ─────────────────────────────────────────────
# Q6: Top 10 highest-rated cuisines (min 50 restaurants)
# ─────────────────────────────────────────────
def q6_highest_rated_cuisines(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(6, "Which cuisines have the highest average ratings? (≥50 restaurants)")
    result = (
        df.groupby(Cols.PRIMARY_CUISINE)
        .agg(count=(Cols.NAME, "count"), avg_rating=(Cols.RATE_NUMERIC, "mean"))
        .query("count >= 50")
        .sort_values("avg_rating", ascending=False)
        .round(3)
        .reset_index()
    )
    print(result.head(10).to_string(index=False))

    top10 = result.head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=top10, y=Cols.PRIMARY_CUISINE, x="avg_rating", palette="RdYlGn", ax=ax)
    ax.set_xlim(3.5, 4.5)
    ax.set_title("Top 10 Highest-Rated Cuisines (≥50 outlets)", fontweight="bold")
    ax.set_xlabel("Average Rating")
    plt.tight_layout()
    save_figure(fig, "q6_highest_rated_cuisines.png", "business")
    return result


# ─────────────────────────────────────────────
# Q7: Location-level avg cost vs avg rating matrix
# ─────────────────────────────────────────────
def q7_location_cost_rating_matrix(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(7, "Which locations offer the best value (high rating, low cost)?")
    result = (
        df.groupby(Cols.LOCATION)
        .agg(
            count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
        )
        .query("count >= 30")
        .reset_index()
        .round(2)
    )
    # Quadrant: High rating (≥ median), Low cost (≤ median) = "Best Value"
    med_r = result["avg_rating"].median()
    med_c = result["avg_cost"].median()
    def quadrant(r, c):
        if r >= med_r and c <= med_c: return "Best Value"
        elif r >= med_r and c > med_c: return "Premium Quality"
        elif r < med_r and c <= med_c: return "Budget Underperformer"
        else: return "Overpriced"
    result["quadrant"] = result.apply(lambda x: quadrant(x["avg_rating"], x["avg_cost"]), axis=1)

    qpal = {"Best Value": "#6FCF97", "Premium Quality": "#2D9CDB", "Budget Underperformer": "#FFB829", "Overpriced": ZOMATO_RED}
    fig, ax = plt.subplots(figsize=(14, 9))
    for quad, grp in result.groupby("quadrant"):
        ax.scatter(grp["avg_cost"], grp["avg_rating"], label=quad,
                   color=qpal[quad], s=80, alpha=0.8)
        for _, row in grp.iterrows():
            if row["count"] > 100:
                ax.annotate(row[Cols.LOCATION], (row["avg_cost"], row["avg_rating"]),
                            fontsize=7, alpha=0.8, xytext=(4, 2), textcoords="offset points")

    ax.axvline(med_c, linestyle="--", color="gray", alpha=0.5)
    ax.axhline(med_r, linestyle="--", color="gray", alpha=0.5)
    ax.set_xlabel("Average Cost for Two (₹)")
    ax.set_ylabel("Average Rating")
    ax.set_title("Location Value Matrix: Rating vs Cost", fontweight="bold")
    ax.legend()
    plt.tight_layout()
    save_figure(fig, "q7_value_matrix.png", "business")
    print(result.groupby("quadrant")["count"].sum().to_string())
    return result


# ─────────────────────────────────────────────
# Q8: Most popular restaurant types by area
# ─────────────────────────────────────────────
def q8_rest_type_by_area(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(8, "What restaurant types dominate in each area?")
    top_locs = df[Cols.LOCATION].value_counts().head(10).index
    top_types = df[Cols.PRIMARY_REST_TYPE].value_counts().head(5).index
    pivot = (
        df[df[Cols.LOCATION].isin(top_locs) & df[Cols.PRIMARY_REST_TYPE].isin(top_types)]
        .groupby([Cols.LOCATION, Cols.PRIMARY_REST_TYPE])[Cols.NAME]
        .count()
        .unstack(fill_value=0)
    )
    print(pivot.to_string())

    fig, ax = plt.subplots(figsize=(14, 7))
    pivot.plot(kind="bar", ax=ax, colormap="Set2", edgecolor="white", alpha=0.9)
    ax.set_title("Restaurant Type Distribution by Top 10 Areas", fontweight="bold")
    ax.set_xlabel("Location")
    ax.set_ylabel("Count")
    plt.xticks(rotation=30, ha="right")
    ax.legend(title="Restaurant Type", loc="upper right")
    plt.tight_layout()
    save_figure(fig, "q8_rest_type_by_area.png", "business")
    return pivot.reset_index()


# ─────────────────────────────────────────────
# Q9: Votes distribution by online order status
# ─────────────────────────────────────────────
def q9_votes_by_online_order(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(9, "Do online-order restaurants get significantly more votes (engagement)?")
    result = (
        df.groupby(Cols.ONLINE_ORDER)
        .agg(
            count=(Cols.NAME, "count"),
            mean_votes=(Cols.VOTES, "mean"),
            median_votes=(Cols.VOTES, "median"),
            total_votes=(Cols.VOTES, "sum"),
        )
        .round(2)
        .reset_index()
    )
    result[Cols.ONLINE_ORDER] = result[Cols.ONLINE_ORDER].map({True: "Online", False: "Offline"})
    print(result.to_string(index=False))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(result[Cols.ONLINE_ORDER], result["mean_votes"], color=[ZOMATO_RED, "#2D9CDB"],
           alpha=0.85, width=0.5)
    ax.set_title("Average Votes: Online vs Offline Restaurants", fontweight="bold")
    ax.set_ylabel("Mean Votes")
    for i, val in enumerate(result["mean_votes"]):
        ax.text(i, val + 5, f"{val:.0f}", ha="center", fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "q9_votes_online_order.png", "business")
    return result


# ─────────────────────────────────────────────
# Q10: Best areas to open a new restaurant
# ─────────────────────────────────────────────
def q10_best_location_to_open(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(10, "Which areas are best to open a new restaurant (low competition, high demand)?")
    result = (
        df.groupby(Cols.LOCATION)
        .agg(
            restaurant_count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            avg_votes=(Cols.VOTES, "mean"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
        )
        .query("restaurant_count >= 20")
        .reset_index()
        .round(2)
    )
    # Opportunity score = avg_votes / restaurant_count * avg_rating
    result["opportunity_score"] = (
        result["avg_votes"] / result["restaurant_count"] * result["avg_rating"]
    ).round(3)
    result = result.sort_values("opportunity_score", ascending=False)
    print(result.head(10).to_string(index=False))
    print(f"\n💡 RECOMMENDATION: Areas with high avg_votes but fewer restaurants signal unmet demand.")

    top10 = result.head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(top10[Cols.LOCATION][::-1], top10["opportunity_score"][::-1],
            color=ZOMATO_PALETTE[4], alpha=0.85)
    ax.set_xlabel("Opportunity Score")
    ax.set_title("Top 10 High-Opportunity Areas for New Restaurants", fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "q10_best_location.png", "business")
    return result


# ─────────────────────────────────────────────
# Q11-Q25: Additional Business Questions (compact)
# ─────────────────────────────────────────────

def q11_service_level_vs_rating(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(11, "Does full-service (online order + table booking) yield better ratings?")
    result = (
        df.groupby("service_level")[Cols.RATE_NUMERIC]
        .agg(["mean", "median", "count"])
        .round(3)
        .reset_index()
    )
    level_map = {0: "No Service", 1: "Online Only", 2: "Booking Only", 3: "Full Service"}
    result["service_level"] = result["service_level"].map(level_map)
    print(result.to_string(index=False))
    return result


def q12_cuisine_diversity_vs_rating(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(12, "Does offering more cuisines improve ratings?")
    result = (
        df.groupby("cuisine_count")
        .agg(avg_rating=(Cols.RATE_NUMERIC, "mean"), count=(Cols.NAME, "count"))
        .query("count >= 20")
        .round(3)
        .reset_index()
    )
    corr = df[["cuisine_count", Cols.RATE_NUMERIC]].dropna().corr().iloc[0, 1]
    print(result.to_string(index=False))
    print(f"\n📊 Correlation: cuisine_count vs rating = {corr:.3f}")
    return result


def q13_segment_profiling(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(13, "What are the distinct restaurant segments (cluster profiles)?")
    if "restaurant_segment" not in df.columns:
        print("⚠️ Run FeatureEngineer.add_restaurant_segments() first.")
        return pd.DataFrame()
    result = (
        df.groupby("restaurant_segment")
        .agg(
            count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
            avg_votes=(Cols.VOTES, "mean"),
            pct_online=(Cols.ONLINE_ORDER, "mean"),
        )
        .round(3)
        .reset_index()
    )
    print(result.to_string(index=False))
    return result


def q14_top_rated_restaurants(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    _print_question(14, f"Who are the top {top_n} highest-rated & most-voted restaurants?")
    result = (
        df[df[Cols.VOTES] >= 500]
        .sort_values([Cols.RATE_NUMERIC, Cols.VOTES], ascending=False)
        [[Cols.NAME, Cols.LOCATION, Cols.PRIMARY_CUISINE, Cols.RATE_NUMERIC, Cols.VOTES, Cols.COST_CLEAN]]
        .head(top_n)
        .reset_index(drop=True)
    )
    print(result.to_string(index=False))
    return result


def q15_cost_by_rest_type(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(15, "What is the typical cost range for each restaurant type?")
    result = (
        df.groupby(Cols.PRIMARY_REST_TYPE)[Cols.COST_CLEAN]
        .describe()
        .round(2)
        .reset_index()
        .sort_values("50%", ascending=False)
    )
    print(result.head(10).to_string(index=False))
    return result


def q16_online_order_penetration_by_area(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(16, "Which areas have the highest online order adoption rates?")
    result = (
        df.groupby(Cols.LOCATION)[Cols.ONLINE_ORDER]
        .mean()
        .mul(100)
        .round(2)
        .sort_values(ascending=False)
        .reset_index()
    )
    result.columns = [Cols.LOCATION, "online_order_pct"]
    print(result.head(10).to_string(index=False))
    return result


def q17_high_rated_cuisine_by_location(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(17, "Which cuisine is rated highest in each major area?")
    top_locs = df[Cols.LOCATION].value_counts().head(10).index
    result = (
        df[df[Cols.LOCATION].isin(top_locs)]
        .groupby([Cols.LOCATION, Cols.PRIMARY_CUISINE])[Cols.RATE_NUMERIC]
        .agg(["mean", "count"])
        .query("count >= 10")
        .reset_index()
        .sort_values([Cols.LOCATION, "mean"], ascending=[True, False])
        .groupby(Cols.LOCATION)
        .first()
        .reset_index()
    )
    print(result[[Cols.LOCATION, Cols.PRIMARY_CUISINE, "mean"]].to_string(index=False))
    return result


def q18_votes_percentile_analysis(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(18, "Votes distribution: what separates viral restaurants from the rest?")
    pcts = [50, 75, 90, 95, 99]
    result = pd.DataFrame({
        "percentile": pcts,
        "votes_threshold": [df[Cols.VOTES].quantile(p/100) for p in pcts]
    })
    print(result.to_string(index=False))
    print(f"\n💡 Only top 1% restaurants cross {df[Cols.VOTES].quantile(0.99):.0f} votes — extreme concentration.")
    return result


def q19_budget_segment_leaders(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(19, "Who leads in the budget segment (cost ≤ ₹300)?")
    result = (
        df[df[Cols.COST_CLEAN] <= 300]
        .sort_values([Cols.RATE_NUMERIC, Cols.VOTES], ascending=False)
        [[Cols.NAME, Cols.LOCATION, Cols.PRIMARY_CUISINE, Cols.RATE_NUMERIC, Cols.VOTES]]
        .head(15)
        .reset_index(drop=True)
    )
    print(result.to_string(index=False))
    return result


def q20_full_service_premium(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(20, "Does full-service cost more? Premium analysis.")
    result = (
        df.groupby([Cols.ONLINE_ORDER, Cols.BOOK_TABLE])[Cols.COST_CLEAN]
        .agg(["mean", "median", "count"])
        .round(2)
        .reset_index()
    )
    result[Cols.ONLINE_ORDER] = result[Cols.ONLINE_ORDER].map({True: "Yes", False: "No"})
    result[Cols.BOOK_TABLE]   = result[Cols.BOOK_TABLE].map({True: "Yes", False: "No"})
    print(result.to_string(index=False))
    return result


def q21_location_cuisine_heatmap_rating(df: pd.DataFrame):
    _print_question(21, "Location × Cuisine: where does each cuisine excel?")
    top_locs     = df[Cols.LOCATION].value_counts().head(8).index
    top_cuisines = df[Cols.PRIMARY_CUISINE].value_counts().head(8).index
    pivot = (
        df[df[Cols.LOCATION].isin(top_locs) & df[Cols.PRIMARY_CUISINE].isin(top_cuisines)]
        .groupby([Cols.LOCATION, Cols.PRIMARY_CUISINE])[Cols.RATE_NUMERIC]
        .mean()
        .unstack()
        .round(2)
    )
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax, vmin=3.0, vmax=4.5)
    ax.set_title("Avg Rating: Location × Cuisine", fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "q21_loc_cuisine_heatmap.png", "business")
    return pivot


def q22_value_for_money_leaders(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(22, "Which restaurants offer best value-for-money? (rating/cost ratio)")
    if "value_for_money" not in df.columns:
        print("⚠️ Run FeatureEngineer.add_value_for_money() first.")
        return pd.DataFrame()
    result = (
        df[df[Cols.VOTES] >= 200]
        .sort_values("value_for_money", ascending=False)
        [[Cols.NAME, Cols.LOCATION, Cols.PRIMARY_CUISINE, Cols.RATE_NUMERIC, Cols.COST_CLEAN, "value_for_money"]]
        .head(15)
        .reset_index(drop=True)
    )
    print(result.to_string(index=False))
    return result


def q23_growth_opportunity_cuisines(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(23, "Which cuisines are under-represented but highly rated? (Market gaps)")
    result = (
        df.groupby(Cols.PRIMARY_CUISINE)
        .agg(count=(Cols.NAME, "count"), avg_rating=(Cols.RATE_NUMERIC, "mean"))
        .query("count < 100 and avg_rating >= 4.0")
        .sort_values("avg_rating", ascending=False)
        .reset_index()
        .round(3)
    )
    print(result.head(15).to_string(index=False))
    print("\n💡 These cuisines have high ratings but low count → Market gaps / expansion opportunities.")
    return result


def q24_high_vote_low_rating_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    _print_question(24, "High-vote but low-rating restaurants: what went wrong?")
    result = (
        df[
            (df[Cols.VOTES] >= df[Cols.VOTES].quantile(0.90)) &
            (df[Cols.RATE_NUMERIC] < 3.5)
        ]
        .sort_values(Cols.VOTES, ascending=False)
        [[Cols.NAME, Cols.LOCATION, Cols.PRIMARY_CUISINE, Cols.RATE_NUMERIC, Cols.VOTES, Cols.COST_CLEAN]]
        .head(15)
        .reset_index(drop=True)
    )
    print(result.to_string(index=False))
    print("\n💡 These are viral but divisive restaurants — potential for quality improvement marketing.")
    return result


def q25_executive_kpi_summary(df: pd.DataFrame) -> dict:
    _print_question(25, "Executive KPI Summary: Bangalore Food Industry Snapshot")
    kpis = {
        "total_restaurants":         len(df),
        "unique_locations":           df[Cols.LOCATION].nunique(),
        "unique_cuisines":            df[Cols.PRIMARY_CUISINE].nunique(),
        "avg_rating":                 round(df[Cols.RATE_NUMERIC].mean(), 3),
        "median_cost_for_two":        round(df[Cols.COST_CLEAN].median(), 0),
        "pct_online_order":           round(df[Cols.ONLINE_ORDER].mean() * 100, 1),
        "pct_table_booking":          round(df[Cols.BOOK_TABLE].mean() * 100, 1),
        "pct_high_rated":             round((df[Cols.RATE_NUMERIC] >= 4.0).mean() * 100, 1),
        "total_votes_recorded":       int(df[Cols.VOTES].sum()),
        "top_location":               df[Cols.LOCATION].value_counts().index[0],
        "top_cuisine":                df[Cols.PRIMARY_CUISINE].value_counts().index[0],
        "top_rest_type":              df[Cols.PRIMARY_REST_TYPE].value_counts().index[0],
    }
    print("\n  EXECUTIVE KPI DASHBOARD")
    print("  " + "─"*40)
    for k, v in kpis.items():
        print(f"  {k:<30}: {v}")
    return kpis


# ─────────────────────────────────────────────
# MASTER RUNNER
# ─────────────────────────────────────────────
def run_all_business_analysis(df: pd.DataFrame) -> dict:
    """Run all 25 business questions and return results dict."""
    results = {}
    results["q1"]  = q1_restaurant_density_by_location(df)
    results["q2"]  = q2_online_order_impact_on_rating(df)
    results["q3"]  = q3_price_rating_sweet_spot(df)
    results["q4"]  = q4_cuisine_premium_pricing(df)
    results["q5"]  = q5_table_booking_impact(df)
    results["q6"]  = q6_highest_rated_cuisines(df)
    results["q7"]  = q7_location_cost_rating_matrix(df)
    results["q8"]  = q8_rest_type_by_area(df)
    results["q9"]  = q9_votes_by_online_order(df)
    results["q10"] = q10_best_location_to_open(df)
    results["q11"] = q11_service_level_vs_rating(df)
    results["q12"] = q12_cuisine_diversity_vs_rating(df)
    results["q13"] = q13_segment_profiling(df)
    results["q14"] = q14_top_rated_restaurants(df)
    results["q15"] = q15_cost_by_rest_type(df)
    results["q16"] = q16_online_order_penetration_by_area(df)
    results["q17"] = q17_high_rated_cuisine_by_location(df)
    results["q18"] = q18_votes_percentile_analysis(df)
    results["q19"] = q19_budget_segment_leaders(df)
    results["q20"] = q20_full_service_premium(df)
    results["q21"] = q21_location_cuisine_heatmap_rating(df)
    results["q22"] = q22_value_for_money_leaders(df)
    results["q23"] = q23_growth_opportunity_cuisines(df)
    results["q24"] = q24_high_vote_low_rating_anomalies(df)
    results["q25"] = q25_executive_kpi_summary(df)
    return results


if __name__ == "__main__":
    from src.utils import load_cleaned_data
    from src.preprocessing import FeatureEngineer
    df = load_cleaned_data()
    df = FeatureEngineer.run_all(df)
    run_all_business_analysis(df)
