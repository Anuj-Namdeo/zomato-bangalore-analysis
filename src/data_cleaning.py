"""
data_cleaning.py — Complete data cleaning pipeline for Zomato Bangalore dataset
Author: Your Name

Pipeline order:
    1. drop_unnamed_columns()
    2. drop_duplicates()
    3. clean_rate_column()
    4. clean_cost_column()
    5. clean_online_order_book_table()
    6. clean_votes()
    7. clean_location()
    8. clean_rest_type()
    9. clean_cuisines()
    10. handle_nulls()
    11. fix_dtypes()
    12. run_full_pipeline()  ← orchestrator
"""

import re
import pandas as pd
import numpy as np
from typing import Tuple, Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import get_logger, Cols, CLEANED_FILE, timer

logger = get_logger("data_cleaning")


# ─────────────────────────────────────────────
# 1. DROP UNNAMED / SYSTEM COLUMNS
# ─────────────────────────────────────────────
def drop_unnamed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove Unnamed:0 artifact columns from CSV export."""
    before = df.shape[1]
    unnamed = [c for c in df.columns if c.startswith("Unnamed")]
    df = df.drop(columns=unnamed, errors="ignore")
    logger.info(f"Dropped {len(unnamed)} unnamed columns → {before} → {df.shape[1]} cols")
    return df


# ─────────────────────────────────────────────
# 2. DUPLICATES
# ─────────────────────────────────────────────
def drop_duplicates(df: pd.DataFrame, subset: Optional[list] = None) -> pd.DataFrame:
    """
    Drop exact duplicates. Strategy:
      - Full-row duplicates are noise (same restaurant listed twice).
      - Keep='first' preserves original ordering.
    """
    before = len(df)
    df = df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
    removed = before - len(df)
    logger.info(f"Duplicates removed: {removed:,} ({removed/before*100:.2f}%) → {len(df):,} rows remain")
    return df


# ─────────────────────────────────────────────
# 3. RATE COLUMN
# ─────────────────────────────────────────────
def clean_rate_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Raw 'rate' examples: '4.1/5', 'NEW', '-', '3.8 /5', NaN
    Strategy:
      - Extract numeric part before '/5'
      - Coerce 'NEW', '-', 'nan' to NaN
      - Clip to valid range [1.0, 5.0]
      - Store as float in new column 'rate_numeric'
    """
    def parse_rate(val) -> Optional[float]:
        if pd.isna(val):
            return np.nan
        val = str(val).strip().upper()
        if val in {"NEW", "-", "NAN", ""}:
            return np.nan
        # e.g. "4.1/5" or "3.8 /5"
        match = re.match(r"^(\d+\.?\d*)\s*/\s*5", val)
        if match:
            r = float(match.group(1))
            return r if 1.0 <= r <= 5.0 else np.nan
        return np.nan

    df[Cols.RATE_NUMERIC] = df[Cols.RATE].apply(parse_rate)
    null_pct = df[Cols.RATE_NUMERIC].isna().mean() * 100
    logger.info(
        f"rate_numeric: {df[Cols.RATE_NUMERIC].notna().sum():,} valid "
        f"| {null_pct:.1f}% null "
        f"| range [{df[Cols.RATE_NUMERIC].min()}, {df[Cols.RATE_NUMERIC].max()}]"
    )
    return df


# ─────────────────────────────────────────────
# 4. APPROXIMATE COST
# ─────────────────────────────────────────────
def clean_cost_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Raw 'approx_cost(for two)' examples: '800', '1,200', '150', NaN
    Strategy:
      - Remove commas, strip whitespace
      - Coerce to float
      - Cap extreme outliers at 99th percentile (>10000 are data entry errors)
      - Store in new column 'approx_cost'
    """
    def parse_cost(val) -> Optional[float]:
        if pd.isna(val):
            return np.nan
        val = str(val).replace(",", "").strip()
        try:
            c = float(val)
            return c if c > 0 else np.nan
        except ValueError:
            return np.nan

    df[Cols.COST_CLEAN] = df[Cols.COST].apply(parse_cost)

    # Cap at 99th percentile
    cap = df[Cols.COST_CLEAN].quantile(0.99)
    n_capped = (df[Cols.COST_CLEAN] > cap).sum()
    df[Cols.COST_CLEAN] = df[Cols.COST_CLEAN].clip(upper=cap)
    
    logger.info(
        f"approx_cost: {df[Cols.COST_CLEAN].notna().sum():,} valid "
        f"| {n_capped} values capped at ₹{cap:.0f} (99th pct) "
        f"| median=₹{df[Cols.COST_CLEAN].median():.0f}"
    )
    return df


# ─────────────────────────────────────────────
# 5. BINARY FLAG COLUMNS
# ─────────────────────────────────────────────
def clean_online_order_book_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    'online_order' and 'book_table': values are 'Yes' / 'No'.
    Convert to bool (True/False) for downstream analysis.
    """
    for col in [Cols.ONLINE_ORDER, Cols.BOOK_TABLE]:
        df[col] = df[col].str.strip().str.upper().map({"YES": True, "NO": False})
        null_count = df[col].isna().sum()
        logger.info(f"{col}: {df[col].sum():,} True | {(~df[col]).sum():,} False | {null_count} null")
    return df


# ─────────────────────────────────────────────
# 6. VOTES
# ─────────────────────────────────────────────
def clean_votes(df: pd.DataFrame) -> pd.DataFrame:
    """
    'votes': already numeric but may have nulls or negatives.
    Fill nulls with 0 (no votes recorded = 0, not missing).
    """
    df[Cols.VOTES] = pd.to_numeric(df[Cols.VOTES], errors="coerce").fillna(0).astype(int)
    logger.info(
        f"votes: range [{df[Cols.VOTES].min()}, {df[Cols.VOTES].max()}] "
        f"| median={df[Cols.VOTES].median():.0f}"
    )
    return df


# ─────────────────────────────────────────────
# 7. LOCATION
# ─────────────────────────────────────────────
# Mapping for common name variants (extend as needed)
LOCATION_NORMALIZATION = {
    "Brigade Road, Central Bangalore": "Brigade Road",
    "Lavelle Road, Central Bangalore": "Lavelle Road",
    "Residency Road, Central Bangalore": "Residency Road",
    "Church Street, Central Bangalore": "Church Street",
    "1 Mg Road, Ashok Nagar": "MG Road",
    "MG Road, Central Bangalore": "MG Road",
    "Indiranagar, East Bangalore": "Indiranagar",
    "Koramangala 5th Block": "Koramangala",
    "Koramangala 6th Block": "Koramangala",
    "Koramangala 7th Block": "Koramangala",
    "Koramangala 4th Block": "Koramangala",
    "Koramangala 1st Block": "Koramangala",
    "Whitefield, East Bangalore": "Whitefield",
    "Electronic City, South Bangalore": "Electronic City",
    "HSR Layout, South Bangalore": "HSR Layout",
    "Marathahalli, East Bangalore": "Marathahalli",
}

def clean_location(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise location names:
      - Strip whitespace
      - Apply normalization map
      - Nullify rare single-occurrence locations (< 5 restaurants) → 'Other'
    """
    df[Cols.LOCATION] = (
        df[Cols.LOCATION]
        .astype(str)
        .str.strip()
        .replace(LOCATION_NORMALIZATION)
    )
    df[Cols.LOCATION] = df[Cols.LOCATION].replace("nan", np.nan)

    # Rare locations → 'Other'
    loc_counts = df[Cols.LOCATION].value_counts()
    rare = loc_counts[loc_counts < 5].index
    n_rare = df[Cols.LOCATION].isin(rare).sum()
    df[Cols.LOCATION] = df[Cols.LOCATION].replace(rare, "Other")
    
    logger.info(
        f"location: {df[Cols.LOCATION].nunique()} unique areas "
        f"| {n_rare} rare locations merged to 'Other'"
    )
    return df


# ─────────────────────────────────────────────
# 8. RESTAURANT TYPE
# ─────────────────────────────────────────────
def clean_rest_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    'rest_type' may contain comma-separated types: 'Quick Bites, Casual Dining'
    Strategy:
      - Create 'primary_rest_type' from first token (most dominant type)
      - Strip and standardize casing
    """
    df[Cols.REST_TYPE] = df[Cols.REST_TYPE].astype(str).str.strip()
    df[Cols.PRIMARY_REST_TYPE] = (
        df[Cols.REST_TYPE]
        .str.split(",")
        .str[0]
        .str.strip()
        .str.title()
        .replace("Nan", np.nan)
    )
    logger.info(
        f"primary_rest_type: {df[Cols.PRIMARY_REST_TYPE].nunique()} unique types "
        f"| top: {df[Cols.PRIMARY_REST_TYPE].value_counts().index[0]}"
    )
    return df


# ─────────────────────────────────────────────
# 9. CUISINES
# ─────────────────────────────────────────────
def clean_cuisines(df: pd.DataFrame) -> pd.DataFrame:
    """
    'cuisines' contains comma-separated list: 'North Indian, Chinese, Biryani'
    Strategy:
      - Clean raw field
      - Extract 'primary_cuisine' (first listed cuisine)
      - Count total cuisines per restaurant
    """
    df[Cols.CUISINES] = df[Cols.CUISINES].astype(str).str.strip()

    df[Cols.PRIMARY_CUISINE] = (
        df[Cols.CUISINES]
        .str.split(",")
        .str[0]
        .str.strip()
        .str.title()
        .replace("Nan", np.nan)
    )

    df["cuisine_count"] = (
        df[Cols.CUISINES]
        .str.split(",")
        .apply(lambda x: len(x) if isinstance(x, list) else 0)
    )

    # Rare cuisines → 'Other'
    cuisine_counts = df[Cols.PRIMARY_CUISINE].value_counts()
    rare = cuisine_counts[cuisine_counts < 10].index
    df[Cols.PRIMARY_CUISINE] = df[Cols.PRIMARY_CUISINE].replace(rare, "Other")

    logger.info(
        f"primary_cuisine: {df[Cols.PRIMARY_CUISINE].nunique()} unique "
        f"| avg cuisines/restaurant: {df['cuisine_count'].mean():.1f}"
    )
    return df


# ─────────────────────────────────────────────
# 10. NULL HANDLING
# ─────────────────────────────────────────────
def handle_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Null strategy by column:
      - rate_numeric   : Keep as NaN (MNAR — new restaurants have no rating)
      - approx_cost    : Fill with median per rest_type group
      - location       : Fill with mode (most common area)
      - cuisines       : Fill with 'Unknown'
      - rest_type      : Fill with 'Unknown'
      - phone          : Drop column (not used in analysis)
      - dish_liked     : Keep NaN (optional field)
      - menu_item      : Drop column (too sparse)
    """
    # Drop phone and menu_item
    cols_to_drop = ["phone", "menu_item"]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors="ignore")
    logger.info(f"Dropped columns: {cols_to_drop}")

    # approx_cost: median per primary_rest_type group
    df[Cols.COST_CLEAN] = df.groupby(Cols.PRIMARY_REST_TYPE)[Cols.COST_CLEAN].transform(
        lambda x: x.fillna(x.median())
    )
    # fallback: overall median
    overall_median = df[Cols.COST_CLEAN].median()
    df[Cols.COST_CLEAN] = df[Cols.COST_CLEAN].fillna(overall_median)

    # location: mode
    loc_mode = df[Cols.LOCATION].mode()[0]
    df[Cols.LOCATION] = df[Cols.LOCATION].fillna(loc_mode)

    # cuisines / rest_type
    df[Cols.PRIMARY_CUISINE]   = df[Cols.PRIMARY_CUISINE].fillna("Unknown")
    df[Cols.PRIMARY_REST_TYPE] = df[Cols.PRIMARY_REST_TYPE].fillna("Unknown")

    remaining_nulls = df.isnull().sum()
    logger.info(f"Remaining nulls:\n{remaining_nulls[remaining_nulls > 0]}")
    return df


# ─────────────────────────────────────────────
# 11. FIX DTYPES & ADD ENGINEERED COLUMNS
# ─────────────────────────────────────────────
def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure correct dtypes and add binned engineered columns.
    """
    # Cost bucket
    df[Cols.COST_BUCKET] = pd.cut(
        df[Cols.COST_CLEAN],
        bins=[0, 300, 600, 1000, 1500, float("inf")],
        labels=["Budget (≤300)", "Mid (301-600)", "Premium (601-1000)", "Upscale (1001-1500)", "Luxury (>1500)"],
    )

    # Votes bucket
    df[Cols.VOTES_BUCKET] = pd.cut(
        df[Cols.VOTES],
        bins=[-1, 10, 100, 500, 1000, float("inf")],
        labels=["New (0-10)", "Growing (11-100)", "Popular (101-500)", "Trendy (501-1000)", "Viral (>1000)"],
    )

    # High rated flag
    df["is_high_rated"] = df[Cols.RATE_NUMERIC] >= 4.0

    logger.info("Dtypes fixed and engineered columns added: cost_bucket, votes_bucket, is_high_rated")
    return df


# ─────────────────────────────────────────────
# 12. ORCHESTRATOR
# ─────────────────────────────────────────────
@timer
def run_full_pipeline(df: pd.DataFrame, save: bool = True) -> pd.DataFrame:
    """
    Execute the complete cleaning pipeline in sequence.
    Returns the cleaned DataFrame and optionally saves to data/cleaned/.
    """
    logger.info("=" * 60)
    logger.info("STARTING DATA CLEANING PIPELINE")
    logger.info("=" * 60)

    df = drop_unnamed_columns(df)
    df = drop_duplicates(df)
    df = clean_rate_column(df)
    df = clean_cost_column(df)
    df = clean_online_order_book_table(df)
    df = clean_votes(df)
    df = clean_location(df)
    df = clean_rest_type(df)
    df = clean_cuisines(df)
    df = handle_nulls(df)
    df = fix_dtypes(df)

    logger.info("=" * 60)
    logger.info(f"PIPELINE COMPLETE → Final shape: {df.shape}")
    logger.info("=" * 60)

    if save:
        CLEANED_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(CLEANED_FILE, index=False, encoding="utf-8")
        logger.info(f"Saved cleaned data → {CLEANED_FILE}")

    return df


# ─────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    from src.utils import load_raw_data
    raw = load_raw_data()
    cleaned = run_full_pipeline(raw, save=True)
    print(f"\nFinal cleaned shape: {cleaned.shape}")
    print(cleaned.dtypes)
