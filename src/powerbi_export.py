"""
powerbi_export.py — Prepare and export data tables for Power BI consumption
Author: Your Name

Exports structured Excel workbook with:
  - Sheet 1: Main cleaned dataset
  - Sheet 2: Location summary table
  - Sheet 3: Cuisine summary table
  - Sheet 4: Restaurant type summary
  - Sheet 5: KPI table (single-row, for card visuals)
  - Sheet 6: Time/Segment pivot

Power BI imports this .xlsx directly for a zero-SQL implementation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import get_logger, Cols, PROJECT_ROOT, timer

logger = get_logger("powerbi_export")

EXPORT_PATH = PROJECT_ROOT / "data" / "cleaned" / "zomato_powerbi.xlsx"


# ─────────────────────────────────────────────
# SUMMARY TABLE BUILDERS
# ─────────────────────────────────────────────
def build_main_table(df: pd.DataFrame) -> pd.DataFrame:
    """Select and rename columns for Power BI main fact table."""
    keep_cols = [
        Cols.NAME, Cols.ONLINE_ORDER, Cols.BOOK_TABLE,
        Cols.RATE_NUMERIC, Cols.VOTES, Cols.LOCATION,
        Cols.PRIMARY_REST_TYPE, Cols.PRIMARY_CUISINE,
        Cols.COST_CLEAN, "cost_bucket", "votes_bucket",
        "is_high_rated", "cuisine_count",
    ]
    keep_cols = [c for c in keep_cols if c in df.columns]
    main = df[keep_cols].copy()
    main.columns = [c.replace("_", " ").title() for c in main.columns]
    return main


def build_location_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregated location dimension table."""
    return (
        df.groupby(Cols.LOCATION)
        .agg(
            restaurant_count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            median_rating=(Cols.RATE_NUMERIC, "median"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
            median_cost=(Cols.COST_CLEAN, "median"),
            total_votes=(Cols.VOTES, "sum"),
            avg_votes=(Cols.VOTES, "mean"),
            online_order_pct=(Cols.ONLINE_ORDER, lambda x: x.mean() * 100),
            book_table_pct=(Cols.BOOK_TABLE, lambda x: x.mean() * 100),
        )
        .round(2)
        .reset_index()
        .sort_values("restaurant_count", ascending=False)
    )


def build_cuisine_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregated cuisine dimension table."""
    return (
        df.groupby(Cols.PRIMARY_CUISINE)
        .agg(
            restaurant_count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
            total_votes=(Cols.VOTES, "sum"),
            pct_online_order=(Cols.ONLINE_ORDER, lambda x: x.mean() * 100),
        )
        .round(2)
        .reset_index()
        .sort_values("restaurant_count", ascending=False)
    )


def build_rest_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregated restaurant type dimension table."""
    return (
        df.groupby(Cols.PRIMARY_REST_TYPE)
        .agg(
            restaurant_count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
            pct_online_order=(Cols.ONLINE_ORDER, lambda x: x.mean() * 100),
            pct_book_table=(Cols.BOOK_TABLE, lambda x: x.mean() * 100),
        )
        .round(2)
        .reset_index()
        .sort_values("restaurant_count", ascending=False)
    )


def build_kpi_table(df: pd.DataFrame) -> pd.DataFrame:
    """Single-row KPI table for Power BI card visuals."""
    return pd.DataFrame([{
        "Total Restaurants":      len(df),
        "Avg Rating":             round(df[Cols.RATE_NUMERIC].mean(), 2),
        "Median Cost For Two":    round(df[Cols.COST_CLEAN].median(), 0),
        "Online Order Pct":       round(df[Cols.ONLINE_ORDER].mean() * 100, 1),
        "Table Booking Pct":      round(df[Cols.BOOK_TABLE].mean() * 100, 1),
        "Pct High Rated (≥4.0)": round((df[Cols.RATE_NUMERIC] >= 4.0).mean() * 100, 1),
        "Total Votes":            int(df[Cols.VOTES].sum()),
        "Unique Locations":       df[Cols.LOCATION].nunique(),
        "Unique Cuisines":        df[Cols.PRIMARY_CUISINE].nunique(),
        "Top Location":           df[Cols.LOCATION].value_counts().index[0],
        "Top Cuisine":            df[Cols.PRIMARY_CUISINE].value_counts().index[0],
        "Top Rest Type":          df[Cols.PRIMARY_REST_TYPE].value_counts().index[0],
    }])


def build_segment_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Cost × RestType pivot for treemap / matrix visual."""
    top_types = df[Cols.PRIMARY_REST_TYPE].value_counts().head(8).index
    top_locs  = df[Cols.LOCATION].value_counts().head(12).index
    return (
        df[df[Cols.PRIMARY_REST_TYPE].isin(top_types) & df[Cols.LOCATION].isin(top_locs)]
        .groupby([Cols.LOCATION, Cols.PRIMARY_REST_TYPE])
        .agg(
            count=(Cols.NAME, "count"),
            avg_rating=(Cols.RATE_NUMERIC, "mean"),
            avg_cost=(Cols.COST_CLEAN, "mean"),
        )
        .round(2)
        .reset_index()
    )


# ─────────────────────────────────────────────
# EXCEL WORKBOOK EXPORTER
# ─────────────────────────────────────────────
@timer
def export_to_excel(df: pd.DataFrame, path: Path = None) -> Path:
    """
    Export all Power BI tables to a structured Excel workbook.
    Each sheet is a named, styled table.
    """
    path = path or EXPORT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    sheets = {
        "Main_Data":        build_main_table(df),
        "Location_Summary": build_location_summary(df),
        "Cuisine_Summary":  build_cuisine_summary(df),
        "RestType_Summary": build_rest_type_summary(df),
        "KPI_Table":        build_kpi_table(df),
        "Segment_Pivot":    build_segment_pivot(df),
    }

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        workbook = writer.book

        # Formats
        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#E23744", "font_color": "white",
            "border": 1, "align": "center",
        })
        number_fmt = workbook.add_format({"num_format": "#,##0.00"})
        int_fmt    = workbook.add_format({"num_format": "#,##0"})

        for sheet_name, sheet_df in sheets.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
            ws = writer.sheets[sheet_name]

            # Header row
            for col_num, col_name in enumerate(sheet_df.columns):
                ws.write(0, col_num, col_name, header_fmt)

            # Column widths
            # for i, col in enumerate(sheet_df.columns):  
            #     try:
            #         max_len = max(
            #             len(str(col)),
            #             sheet_df[col]
            #             .fillna("")
            #             .astype(str)
            #             .apply(lambda x: len(x))
            #             .max()
            #         )
            #         ws.set_column(i, i, min(max_len + 4, 40))
            #     except Exception as e:
            #         logger.warning(f"Could not auto-size column {col}: {e}")
            #         ws.set_column(i, i, 20)
            #     logger.info(f"Power BI export saved: {path}")
            #     return path

            for i, col in enumerate(sheet_df.columns):
                try:
                    max_len = max(
                        len(str(col)),
                        sheet_df[col].fillna("").astype(str).map(len).max()
                    )
                    ws.set_column(i, i, min(max_len + 4, 40))
                except Exception as e:
                    logger.warning(f"Could not auto-size column {col}: {e}")
                    ws.set_column(i, i, 20)

            logger.info(f"Power BI export saved: {path}")

            return path
# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────
if __name__ == "__main__":
    from src.utils import load_cleaned_data
    from src.preprocessing import FeatureEngineer
    df = load_cleaned_data()
    df = FeatureEngineer.run_all(df)
    export_path = export_to_excel(df)
    print(f"\n✅ Power BI Excel exported: {export_path}")
    print("Next: Open Power BI Desktop → Get Data → Excel → select zomato_powerbi.xlsx")
