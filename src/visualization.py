"""
visualization.py — Advanced / composite visualization functions
Author: Your Name

Builds multi-panel dashboards and summary visuals
suitable for final reports and LinkedIn post screenshots.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import folium
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import (
    get_logger, Cols, save_figure, set_plot_style, ZOMATO_PALETTE, ZOMATO_RED
)

logger = get_logger("visualization")
set_plot_style()


# ─────────────────────────────────────────────
# EXECUTIVE DASHBOARD (4-panel)
# ─────────────────────────────────────────────
def plot_executive_dashboard(df: pd.DataFrame) -> plt.Figure:
    """
    4-panel composite figure suitable for report cover / LinkedIn post.
    Panels: Rating dist | Top Locations | Online Order split | Price segments
    """
    fig = plt.figure(figsize=(18, 12), facecolor="white")
    gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35)

    # Panel 1: Rating distribution
    ax1 = fig.add_subplot(gs[0, 0])
    rate = df[Cols.RATE_NUMERIC].dropna()
    ax1.hist(rate, bins=35, color=ZOMATO_RED, alpha=0.85, edgecolor="white")
    ax1.axvline(rate.mean(), color="navy", linestyle="--", linewidth=1.5, label=f"Mean {rate.mean():.2f}")
    ax1.set_title("Rating Distribution", fontweight="bold")
    ax1.set_xlabel("Rating"); ax1.set_ylabel("Count"); ax1.legend(fontsize=8)

    # Panel 2: Top 10 Locations
    ax2 = fig.add_subplot(gs[0, 1:])
    top10 = df[Cols.LOCATION].value_counts().head(10)
    ax2.barh(top10.index[::-1], top10.values[::-1], color=sns.color_palette("RdYlBu_r", 10))
    ax2.set_title("Top 10 Locations by Restaurant Count", fontweight="bold")
    ax2.set_xlabel("Count")

    # Panel 3: Online Order pie
    ax3 = fig.add_subplot(gs[1, 0])
    counts = df[Cols.ONLINE_ORDER].value_counts()
    ax3.pie(counts.values, labels=["Online", "Offline"],
            colors=[ZOMATO_RED, "#2D9CDB"], autopct="%1.0f%%",
            startangle=90, wedgeprops={"edgecolor": "white"})
    ax3.set_title("Online Order Split", fontweight="bold")

    # Panel 4: Cost buckets
    ax4 = fig.add_subplot(gs[1, 1])
    bucket_order = ["Budget (≤300)", "Mid (301-600)", "Premium (601-1000)", "Upscale (1001-1500)", "Luxury (>1500)"]
    bucket_counts = df[Cols.COST_BUCKET].value_counts().reindex(bucket_order)
    ax4.bar(range(len(bucket_order)), bucket_counts.values,
            color=ZOMATO_PALETTE[:5], edgecolor="white", alpha=0.9)
    ax4.set_xticks(range(len(bucket_order)))
    ax4.set_xticklabels(["Budget", "Mid", "Premium", "Upscale", "Luxury"], rotation=15)
    ax4.set_title("Restaurants by Price Segment", fontweight="bold")
    ax4.set_ylabel("Count")

    # Panel 5: Top cuisines
    ax5 = fig.add_subplot(gs[1, 2])
    top_c = df[Cols.PRIMARY_CUISINE].value_counts().head(8)
    ax5.barh(top_c.index[::-1], top_c.values[::-1],
             color=sns.color_palette("Set2", 8))
    ax5.set_title("Top 8 Cuisines", fontweight="bold")
    ax5.set_xlabel("Count")

    fig.suptitle(
        "Zomato Bangalore — Restaurant Industry Dashboard",
        fontsize=18, fontweight="bold", y=1.01, color="#E23744"
    )

    save_figure(fig, "executive_dashboard.png", "")
    logger.info("Executive dashboard saved.")
    return fig


# ─────────────────────────────────────────────
# FOLIUM INTERACTIVE MAP
# ─────────────────────────────────────────────
BANGALORE_COORDS = {
    "Koramangala":    (12.9352, 77.6245),
    "Indiranagar":    (12.9784, 77.6408),
    "BTM Layout":     (12.9165, 77.6101),
    "Whitefield":     (12.9698, 77.7499),
    "Jayanagar":      (12.9308, 77.5931),
    "HSR Layout":     (12.9116, 77.6389),
    "Marathahalli":   (12.9561, 77.7010),
    "Electronic City":(12.8458, 77.6603),
    "MG Road":        (12.9756, 77.6074),
    "Brigade Road":   (12.9719, 77.6073),
    "Malleshwaram":   (13.0034, 77.5706),
    "JP Nagar":       (12.9077, 77.5850),
    "Bannerghatta Road": (12.8880, 77.5975),
    "Yelahanka":      (13.1006, 77.5963),
    "Hebbal":         (13.0354, 77.5956),
    "Old Airport Road": (12.9600, 77.6480),
    "Lavelle Road":   (12.9718, 77.6021),
    "Church Street":  (12.9737, 77.6074),
    "Richmond Road":  (12.9635, 77.6037),
    "Sarjapur Road":  (12.9088, 77.6797),
}

def generate_location_map(df: pd.DataFrame, save_path: str = None) -> folium.Map:
    """
    Generate an interactive Folium map of Bangalore restaurants.
    Circle size = restaurant count, colour gradient = avg rating.
    """
    loc_stats = (
        df.groupby(Cols.LOCATION)
        .agg(
            count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
        )
        .reset_index()
        .round(2)
    )

    m = folium.Map(location=[12.9716, 77.5946], zoom_start=11, tiles="CartoDB positron")

    for _, row in loc_stats.iterrows():
        coords = BANGALORE_COORDS.get(row[Cols.LOCATION])
        if not coords:
            continue
        rating = row["avg_rating"] if not pd.isna(row["avg_rating"]) else 3.5
        color  = "#E23744" if rating >= 4.0 else "#FC6B21" if rating >= 3.5 else "#FFB829"
        radius = max(10, min(40, row["count"] / 20))

        folium.CircleMarker(
            location=coords,
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(
                f"<b>{row[Cols.LOCATION]}</b><br>"
                f"Restaurants: {int(row['count'])}<br>"
                f"Avg Rating: {rating:.2f}<br>"
                f"Avg Cost: ₹{row['avg_cost']:.0f}",
                max_width=200,
            ),
            tooltip=row[Cols.LOCATION],
        ).add_to(m)

    if save_path is None:
        out = Path(__file__).resolve().parent.parent / "images" / "bangalore_restaurant_map.html"
    else:
        out = Path(save_path)
    m.save(str(out))
    logger.info(f"Interactive map saved: {out}")
    return m


# ─────────────────────────────────────────────
# KPI CARDS (Matplotlib)
# ─────────────────────────────────────────────
def plot_kpi_cards(df: pd.DataFrame) -> plt.Figure:
    """Render KPI summary as styled card-style matplotlib figure."""
    kpis = [
        ("Total Restaurants", f"{len(df):,}", ZOMATO_RED),
        ("Avg Rating",         f"{df[Cols.RATE_NUMERIC].mean():.2f} / 5.0", "#FC6B21"),
        ("Median Cost (2)",    f"₹{df[Cols.COST_CLEAN].median():.0f}", "#FFB829"),
        ("Online Order %",     f"{df[Cols.ONLINE_ORDER].mean()*100:.1f}%", "#2D9CDB"),
        ("Table Booking %",    f"{df[Cols.BOOK_TABLE].mean()*100:.1f}%", "#6FCF97"),
        ("Unique Locations",   f"{df[Cols.LOCATION].nunique()}", "#9B51E0"),
    ]
    fig, axes = plt.subplots(1, 6, figsize=(20, 4), facecolor="#F5F5F5")
    for ax, (label, value, color) in zip(axes, kpis):
        ax.set_facecolor(color)
        ax.text(0.5, 0.6, value, ha="center", va="center", fontsize=22,
                fontweight="bold", color="white", transform=ax.transAxes)
        ax.text(0.5, 0.2, label, ha="center", va="center", fontsize=10,
                color="white", transform=ax.transAxes, wrap=True)
        ax.axis("off")
    fig.suptitle("Zomato Bangalore — Key Performance Indicators", fontweight="bold",
                 fontsize=14, y=1.05)
    plt.tight_layout(pad=0.5)
    save_figure(fig, "kpi_cards.png", "")
    return fig


# ─────────────────────────────────────────────
# RATING RADAR CHART BY SEGMENT
# ─────────────────────────────────────────────
def plot_segment_radar(df: pd.DataFrame) -> plt.Figure:
    """Radar chart comparing restaurant segments across 5 dimensions."""
    if "restaurant_segment" not in df.columns:
        logger.warning("restaurant_segment not found. Run FeatureEngineer first.")
        return None

    categories = ["Avg Rating", "Avg Cost (norm)", "Avg Votes (norm)",
                  "Online Order %", "Table Booking %"]
    segments = df["restaurant_segment"].unique()

    def normalize(series):
        return (series - series.min()) / (series.max() - series.min())

    records = []
    for seg in segments:
        g = df[df["restaurant_segment"] == seg]
        records.append({
            "segment":        seg,
            "Avg Rating":     g[Cols.RATE_NUMERIC].mean(),
            "Avg Cost (norm)": g[Cols.COST_CLEAN].mean(),
            "Avg Votes (norm)": g[Cols.VOTES].mean(),
            "Online Order %": g[Cols.ONLINE_ORDER].mean(),
            "Table Booking %": g[Cols.BOOK_TABLE].mean(),
        })
    seg_df = pd.DataFrame(records).set_index("segment")
    # normalize each column
    for col in categories:
        seg_df[col] = normalize(seg_df[col])

    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    for i, seg in enumerate(seg_df.index):
        values = seg_df.loc[seg, categories].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, label=seg, color=ZOMATO_PALETTE[i % 6])
        ax.fill(angles, values, alpha=0.1, color=ZOMATO_PALETTE[i % 6])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_title("Restaurant Segment Radar Chart", fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    save_figure(fig, "segment_radar.png", "")
    return fig


# ─────────────────────────────────────────────
# MASTER RUNNER
# ─────────────────────────────────────────────
def run_all_visualizations(df: pd.DataFrame):
    """Generate all visualization outputs."""
    plot_kpi_cards(df)
    plot_executive_dashboard(df)
    generate_location_map(df)
    plot_segment_radar(df)
    logger.info("All visualizations complete.")


if __name__ == "__main__":
    from src.utils import load_cleaned_data
    from src.preprocessing import FeatureEngineer
    df = load_cleaned_data()
    df = FeatureEngineer.run_all(df)
    run_all_visualizations(df)
