"""
eda.py — Exploratory Data Analysis visualizations for Zomato Bangalore
Author: Your Name

All functions:
  - Accept a cleaned DataFrame
  - Return (fig, ax) for inline notebook display
  - Auto-save to images/ directory
  - Print key insights to stdout
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from typing import Optional, Tuple
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import (
    get_logger, Cols, save_figure, set_plot_style,
    ZOMATO_PALETTE, ZOMATO_RED, value_counts_pct,
    timer
)

logger = get_logger("eda")
set_plot_style()


# ─────────────────────────────────────────────
# 1. MISSING DATA HEATMAP
# ─────────────────────────────────────────────
def plot_missing_data(df: pd.DataFrame) -> Tuple[plt.Figure, plt.Axes]:
    """Visualize null distribution across columns using missingno-style bar chart."""
    null_pct = (df.isnull().mean() * 100).sort_values(ascending=False)
    null_pct = null_pct[null_pct > 0]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(null_pct.index, null_pct.values, color=ZOMATO_RED, alpha=0.8)
    ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)
    ax.set_xlabel("Missing Percentage (%)")
    ax.set_title("Missing Data Distribution per Column", fontweight="bold")
    ax.set_xlim(0, null_pct.max() * 1.2)
    plt.tight_layout()
    save_figure(fig, "01_missing_data.png", "eda")
    logger.info(f"Top null column: {null_pct.index[0]} ({null_pct.iloc[0]:.1f}%)")
    return fig, ax


# ─────────────────────────────────────────────
# 2. RATING DISTRIBUTION
# ─────────────────────────────────────────────
def plot_rating_distribution(df: pd.DataFrame) -> Tuple[plt.Figure, plt.Axes]:
    """KDE + histogram of restaurant ratings."""
    rate = df[Cols.RATE_NUMERIC].dropna()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    axes[0].hist(rate, bins=40, color=ZOMATO_RED, alpha=0.8, edgecolor="white")
    axes[0].axvline(rate.mean(), color="navy", linestyle="--", label=f"Mean: {rate.mean():.2f}")
    axes[0].axvline(rate.median(), color="gold", linestyle="-.", label=f"Median: {rate.median():.2f}")
    axes[0].set_title("Rating Distribution (Histogram)")
    axes[0].set_xlabel("Rating")
    axes[0].set_ylabel("Count")
    axes[0].legend()

    # KDE
    sns.kdeplot(rate, ax=axes[1], fill=True, color=ZOMATO_RED, alpha=0.5)
    axes[1].set_title("Rating Distribution (KDE)")
    axes[1].set_xlabel("Rating")
    axes[1].set_ylabel("Density")

    fig.suptitle("Restaurant Rating Distribution — Bangalore", fontweight="bold", fontsize=14)
    plt.tight_layout()
    save_figure(fig, "02_rating_distribution.png", "eda")

    insight = (
        f"Rating: Mean={rate.mean():.2f}, Median={rate.median():.2f}, "
        f"Std={rate.std():.2f} | {(rate >= 4.0).mean()*100:.1f}% restaurants rated ≥ 4.0"
    )
    logger.info(insight)
    print(f"\n📊 INSIGHT: {insight}")
    return fig, axes


# ─────────────────────────────────────────────
# 3. TOP LOCATIONS BY RESTAURANT COUNT
# ─────────────────────────────────────────────
def plot_top_locations(df: pd.DataFrame, top_n: int = 20) -> Tuple[plt.Figure, plt.Axes]:
    """Horizontal bar chart of top N locations by restaurant count."""
    top_locs = df[Cols.LOCATION].value_counts().head(top_n)
    colors = [ZOMATO_RED if i == 0 else "#FC6B21" if i < 3 else "#FFB829" for i in range(top_n)]

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(top_locs.index[::-1], top_locs.values[::-1], color=colors[::-1])
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_xlabel("Number of Restaurants")
    ax.set_title(f"Top {top_n} Locations by Restaurant Count", fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "03_top_locations.png", "eda")

    insight = f"Top area: {top_locs.index[0]} ({top_locs.iloc[0]:,} restaurants)"
    logger.info(insight)
    print(f"\n📊 INSIGHT: {insight}")
    return fig, ax


# ─────────────────────────────────────────────
# 4. ONLINE ORDER vs RATING
# ─────────────────────────────────────────────
def plot_online_order_vs_rating(df: pd.DataFrame) -> Tuple[plt.Figure, plt.Axes]:
    """Violin + box plot comparing ratings for online vs offline order restaurants."""
    df_plot = df[[Cols.ONLINE_ORDER, Cols.RATE_NUMERIC]].dropna()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Violin
    sns.violinplot(
        data=df_plot, x=Cols.ONLINE_ORDER, y=Cols.RATE_NUMERIC,
        palette={"True": ZOMATO_RED, "False": "#2D9CDB"},
        inner="quartile", ax=axes[0]
    )
    axes[0].set_title("Rating Distribution: Online Order Available vs Not")
    axes[0].set_xlabel("Accepts Online Order")
    axes[0].set_ylabel("Rating")

    # Count pie
    counts = df[Cols.ONLINE_ORDER].value_counts()
    axes[1].pie(
        counts.values, labels=["Yes", "No"],
        colors=[ZOMATO_RED, "#2D9CDB"], autopct="%1.1f%%",
        startangle=140, explode=[0.05, 0]
    )
    axes[1].set_title("Online Order Availability Split")

    fig.suptitle("Online Order vs Restaurant Rating", fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "04_online_order_vs_rating.png", "eda")

    grp = df_plot.groupby(Cols.ONLINE_ORDER)[Cols.RATE_NUMERIC].mean()
    insight = f"Avg rating — Online: {grp.get(True, 0):.2f} | Offline: {grp.get(False, 0):.2f}"
    print(f"\n📊 INSIGHT: {insight}")
    return fig, axes


# ─────────────────────────────────────────────
# 5. COST DISTRIBUTION
# ─────────────────────────────────────────────
def plot_cost_distribution(df: pd.DataFrame) -> Tuple[plt.Figure, plt.Axes]:
    """Box plots of cost across restaurant types."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Overall histogram
    axes[0].hist(
        df[Cols.COST_CLEAN].dropna(), bins=50,
        color="#FC6B21", alpha=0.85, edgecolor="white"
    )
    axes[0].set_title("Approximate Cost for Two — Distribution")
    axes[0].set_xlabel("Cost (₹)")
    axes[0].set_ylabel("Frequency")
    median_cost = df[Cols.COST_CLEAN].median()
    axes[0].axvline(median_cost, color="red", linestyle="--", label=f"Median: ₹{median_cost:.0f}")
    axes[0].legend()

    # Box by cost bucket
    bucket_order = ["Budget (≤300)", "Mid (301-600)", "Premium (601-1000)", "Upscale (1001-1500)", "Luxury (>1500)"]
    bucket_counts = df[Cols.COST_BUCKET].value_counts().reindex(bucket_order)
    axes[1].bar(
        range(len(bucket_order)),
        bucket_counts.values,
        color=ZOMATO_PALETTE[:5], alpha=0.85, edgecolor="white"
    )
    axes[1].set_xticks(range(len(bucket_order)))
    axes[1].set_xticklabels(bucket_order, rotation=30, ha="right")
    axes[1].set_title("Restaurants by Price Segment")
    axes[1].set_ylabel("Count")

    fig.suptitle("Bangalore Restaurant Price Analysis", fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "05_cost_distribution.png", "eda")
    return fig, axes


# ─────────────────────────────────────────────
# 6. TOP CUISINES
# ─────────────────────────────────────────────
def plot_top_cuisines(df: pd.DataFrame, top_n: int = 15) -> Tuple[plt.Figure, plt.Axes]:
    """Bar chart of top N primary cuisines."""
    top_cuisines = df[Cols.PRIMARY_CUISINE].value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = sns.color_palette("RdYlBu_r", top_n)
    bars = ax.bar(top_cuisines.index, top_cuisines.values, color=colors, edgecolor="white")
    ax.bar_label(bars, padding=2, fontsize=9)
    ax.set_title(f"Top {top_n} Cuisines in Bangalore", fontweight="bold")
    ax.set_xlabel("Cuisine")
    ax.set_ylabel("Number of Restaurants")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    save_figure(fig, "06_top_cuisines.png", "eda")
    return fig, ax


# ─────────────────────────────────────────────
# 7. RESTAURANT TYPE DISTRIBUTION
# ─────────────────────────────────────────────
def plot_rest_type_distribution(df: pd.DataFrame) -> Tuple[plt.Figure, plt.Axes]:
    """Donut chart of restaurant types."""
    rt = df[Cols.PRIMARY_REST_TYPE].value_counts().head(10)

    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(
        rt.values, labels=rt.index,
        autopct="%1.1f%%", startangle=90,
        colors=sns.color_palette("Set2", len(rt)),
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        pctdistance=0.82
    )
    # Donut hole
    center_circle = plt.Circle((0, 0), 0.60, fc="white")
    ax.add_artist(center_circle)
    ax.set_title("Restaurant Type Distribution", fontweight="bold", fontsize=14)
    plt.tight_layout()
    save_figure(fig, "07_rest_type_distribution.png", "eda")
    return fig, ax


# ─────────────────────────────────────────────
# 8. CORRELATION HEATMAP
# ─────────────────────────────────────────────
def plot_correlation_heatmap(df: pd.DataFrame) -> Tuple[plt.Figure, plt.Axes]:
    """Correlation heatmap of key numeric features."""
    num_cols = [Cols.RATE_NUMERIC, Cols.VOTES, Cols.COST_CLEAN,
                "cuisine_count", "popularity_score", "value_for_money"]
    num_cols = [c for c in num_cols if c in df.columns]
    corr = df[num_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="RdYlGn",
        mask=mask, ax=ax, linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        vmin=-1, vmax=1
    )
    ax.set_title("Feature Correlation Heatmap", fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "08_correlation_heatmap.png", "eda")
    return fig, ax


# ─────────────────────────────────────────────
# 9. VOTES vs RATING SCATTER
# ─────────────────────────────────────────────
def plot_votes_vs_rating(df: pd.DataFrame, sample_n: int = 5000) -> Tuple[plt.Figure, plt.Axes]:
    """Scatter plot of votes vs rating, coloured by cost bucket."""
    df_plot = df[[Cols.VOTES, Cols.RATE_NUMERIC, Cols.COST_BUCKET]].dropna().sample(
        min(sample_n, len(df)), random_state=42
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    buckets = df_plot[Cols.COST_BUCKET].unique()
    palette = dict(zip(buckets, ZOMATO_PALETTE[:len(buckets)]))

    for bucket, grp in df_plot.groupby(Cols.COST_BUCKET):
        ax.scatter(
            grp[Cols.VOTES], grp[Cols.RATE_NUMERIC],
            alpha=0.3, s=15, label=str(bucket), color=palette.get(bucket, "gray")
        )

    ax.set_xscale("log")
    ax.set_xlabel("Votes (log scale)")
    ax.set_ylabel("Rating")
    ax.set_title("Votes vs Rating (coloured by price segment)", fontweight="bold")
    ax.legend(title="Cost Bucket", loc="lower right", markerscale=2)
    plt.tight_layout()
    save_figure(fig, "09_votes_vs_rating.png", "eda")
    return fig, ax


# ─────────────────────────────────────────────
# 10. LOCATION × RATING HEATMAP
# ─────────────────────────────────────────────
def plot_location_rating_heatmap(df: pd.DataFrame, top_n: int = 20) -> Tuple[plt.Figure, plt.Axes]:
    """Heatmap of avg rating × restaurant type for top locations."""
    top_locs = df[Cols.LOCATION].value_counts().head(top_n).index
    top_types = df[Cols.PRIMARY_REST_TYPE].value_counts().head(6).index

    pivot = (
        df[df[Cols.LOCATION].isin(top_locs) & df[Cols.PRIMARY_REST_TYPE].isin(top_types)]
        .groupby([Cols.LOCATION, Cols.PRIMARY_REST_TYPE])[Cols.RATE_NUMERIC]
        .mean()
        .unstack(fill_value=np.nan)
    )

    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        pivot, annot=True, fmt=".1f", cmap="YlOrRd",
        ax=ax, linewidths=0.3, cbar_kws={"label": "Avg Rating"},
        vmin=3.0, vmax=4.5
    )
    ax.set_title("Average Rating: Location × Restaurant Type", fontweight="bold")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    save_figure(fig, "10_location_rating_heatmap.png", "eda")
    return fig, ax


# ─────────────────────────────────────────────
# MASTER EDA RUNNER
# ─────────────────────────────────────────────
@timer
def run_full_eda(df: pd.DataFrame):
    """Execute all EDA plots sequentially."""
    print("\n" + "="*60)
    print("  ZOMATO BANGALORE — FULL EDA")
    print("="*60)

    plot_missing_data(df)
    plot_rating_distribution(df)
    plot_top_locations(df)
    plot_online_order_vs_rating(df)
    plot_cost_distribution(df)
    plot_top_cuisines(df)
    plot_rest_type_distribution(df)
    plot_correlation_heatmap(df)
    plot_votes_vs_rating(df)
    plot_location_rating_heatmap(df)

    print("\n✅ All EDA plots saved to images/eda/")


if __name__ == "__main__":
    from src.utils import load_cleaned_data
    df = load_cleaned_data()
    run_full_eda(df)
