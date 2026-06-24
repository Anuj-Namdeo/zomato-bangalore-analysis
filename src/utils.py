"""
utils.py — Shared utilities for Zomato Bangalore Analysis
Author: Your Name
"""

import os
import logging
import json
import time
from pathlib import Path
from typing import Optional, Union
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime

# ─────────────────────────────────────────────
# PROJECT PATHS
# ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW      = PROJECT_ROOT / "data" / "raw"
DATA_CLEANED  = PROJECT_ROOT / "data" / "cleaned"
IMAGES_DIR    = PROJECT_ROOT / "images"
REPORTS_DIR   = PROJECT_ROOT / "reports"
SQL_DIR       = PROJECT_ROOT / "sql"

for _dir in [DATA_RAW, DATA_CLEANED, IMAGES_DIR, REPORTS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

RAW_FILE     = DATA_RAW / "zomato.csv"
CLEANED_FILE = DATA_CLEANED / "zomato_cleaned.csv"


# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger with both file and console handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File
    log_path = PROJECT_ROOT / "logs"
    log_path.mkdir(exist_ok=True)
    fh = logging.FileHandler(log_path / f"{name}.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
def load_raw_data(filepath: Optional[Path] = None, encoding: str = "latin-1") -> pd.DataFrame:
    """Load raw Zomato CSV with error handling and basic validation."""
    path = filepath or RAW_FILE
    logger = get_logger("utils")
    logger.info(f"Loading raw data from: {path}")
    
    if not path.exists():
        raise FileNotFoundError(
            f"Raw data not found at {path}.\n"
            "Download from: https://www.kaggle.com/datasets/himanshupoddar/zomato-bangalore-restaurants\n"
            "Place zomato.csv inside data/raw/"
        )
    
    df = pd.read_csv(path, encoding=encoding)
    logger.info(f"Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    return df


# def load_cleaned_data(filepath: Optional[Path] = None) -> pd.DataFrame:
#     """Load cleaned Zomato CSV."""
#     path = filepath or CLEANED_FILE
#     logger = get_logger("utils")
#     if not path.exists():
#         raise FileNotFoundError(
#             f"Cleaned data not found at {path}. Run 02_Data_Cleaning.ipynb first."
#         )
#     df = pd.read_csv(path, encoding="utf-8")
#     logger.info(f"Loaded cleaned data: {df.shape[0]:,} rows × {df.shape[1]} columns")
#     return df
def load_cleaned_data(path="data/cleaned/zomato_cleaned.csv"):
    df_iter = pd.read_csv(
        path,
        encoding="utf-8",
        chunksize=100_000,
        low_memory=True,
        on_bad_lines="skip"
    )

    df = pd.concat(df_iter, ignore_index=True)
    return df

# ─────────────────────────────────────────────
# DATA INSPECTION HELPERS
# ─────────────────────────────────────────────
def dataframe_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a rich summary DataFrame: dtype, null count/%, unique count, sample values.
    """
    summary = pd.DataFrame({
        "dtype":        df.dtypes,
        "null_count":   df.isnull().sum(),
        "null_pct":     (df.isnull().sum() / len(df) * 100).round(2),
        "unique_count": df.nunique(),
        "sample_val":   [df[c].dropna().iloc[0] if df[c].notna().any() else None for c in df.columns],
    })
    summary["null_pct"] = summary["null_pct"].apply(lambda x: f"{x:.2f}%")
    return summary


def check_duplicates(df: pd.DataFrame, subset: Optional[list] = None) -> dict:
    """Return duplicate analysis dict."""
    total_dups = df.duplicated(subset=subset).sum()
    return {
        "total_rows":       len(df),
        "duplicate_rows":   int(total_dups),
        "duplicate_pct":    round(total_dups / len(df) * 100, 2),
        "unique_rows":      len(df) - int(total_dups),
    }


def outlier_summary(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """IQR-based outlier detection summary."""
    records = []
    for col in cols:
        s = df[col].dropna()
        Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        n_out = ((s < lower) | (s > upper)).sum()
        records.append({
            "column":    col,
            "Q1":        round(Q1, 2),
            "Q3":        round(Q3, 2),
            "IQR":       round(IQR, 2),
            "lower_fence": round(lower, 2),
            "upper_fence": round(upper, 2),
            "outlier_count": int(n_out),
            "outlier_pct":   round(n_out / len(s) * 100, 2),
        })
    return pd.DataFrame(records)


# ─────────────────────────────────────────────
# PLOT STYLING
# ─────────────────────────────────────────────
ZOMATO_PALETTE = ["#E23744", "#FC6B21", "#FFB829", "#2D9CDB", "#6FCF97", "#9B51E0"]
ZOMATO_RED     = "#E23744"

def set_plot_style():
    """Apply consistent Zomato-themed plot style."""
    plt.style.use("seaborn-v0_8-whitegrid")
    matplotlib.rcParams.update({
        "figure.dpi":        120,
        "figure.facecolor":  "white",
        "axes.facecolor":    "#FAFAFA",
        "axes.edgecolor":    "#DDDDDD",
        "axes.labelsize":    12,
        "axes.titlesize":    14,
        "axes.titleweight":  "bold",
        "xtick.labelsize":   10,
        "ytick.labelsize":   10,
        "legend.fontsize":   10,
        "font.family":       "DejaVu Sans",
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


def save_figure(fig: plt.Figure, filename: str, subdir: str = "", dpi: int = 150):
    """Save matplotlib figure to images/ directory."""
    out_dir = IMAGES_DIR / subdir if subdir else IMAGES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / filename
    fig.savefig(filepath, dpi=dpi, bbox_inches="tight", facecolor="white")
    get_logger("utils").info(f"Figure saved: {filepath}")
    return filepath


# ─────────────────────────────────────────────
# COLUMN NAME CONSTANTS
# ─────────────────────────────────────────────
class Cols:
    """Centralised column name registry to prevent typos."""
    NAME          = "name"
    ONLINE_ORDER  = "online_order"
    BOOK_TABLE    = "book_table"
    RATE          = "rate"
    VOTES         = "votes"
    PHONE         = "phone"
    LOCATION      = "location"
    REST_TYPE     = "rest_type"
    DISH_LIKED    = "dish_liked"
    CUISINES      = "cuisines"
    COST          = "approx_cost(for two people)"
    COST_CLEAN    = "approx_cost"
    MENU_ITEM     = "menu_item"
    LISTED_IN_TYPE = "listed_in(type)"
    LISTED_IN_CITY = "listed_in(city)"
    # Engineered
    RATE_NUMERIC  = "rate_numeric"
    COST_BUCKET   = "cost_bucket"
    VOTES_BUCKET  = "votes_bucket"
    PRIMARY_CUISINE = "primary_cuisine"
    PRIMARY_REST_TYPE = "primary_rest_type"


# ─────────────────────────────────────────────
# TIMING DECORATOR
# ─────────────────────────────────────────────
def timer(func):
    """Decorator to log function execution time."""
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        get_logger("timer").info(f"{func.__name__} completed in {elapsed:.3f}s")
        return result
    return wrapper


# ─────────────────────────────────────────────
# REPORT HELPERS
# ─────────────────────────────────────────────
def df_to_markdown(df: pd.DataFrame, max_rows: int = 20) -> str:
    """Convert DataFrame to GitHub-flavoured Markdown table."""
    return df.head(max_rows).to_markdown(index=False)


def print_section(title: str, char: str = "═", width: int = 60):
    """Print a formatted section header."""
    bar = char * width
    print(f"\n{bar}\n  {title}\n{bar}")


def value_counts_pct(series: pd.Series, n: int = 10) -> pd.DataFrame:
    """Return value_counts with percentage column."""
    vc = series.value_counts().head(n)
    pct = (vc / len(series) * 100).round(2)
    return pd.DataFrame({"count": vc, "pct": pct})
