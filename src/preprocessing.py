"""
preprocessing.py — Feature engineering & statistical preprocessing
Author: Your Name

Modules:
    - FeatureEngineer   : Derives new analytical columns
    - StatisticalPrep   : Normalisation, encoding for ML
    - DataValidator     : Schema & constraint validation
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from typing import Tuple, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import get_logger, Cols, timer

logger = get_logger("preprocessing")


# ─────────────────────────────────────────────
# FEATURE ENGINEERING
# ─────────────────────────────────────────────
class FeatureEngineer:
    """
    Derives business-relevant features from cleaned Zomato data.
    All methods are pure (return new DataFrame, no in-place mutation).
    """

    @staticmethod
    @timer
    def add_popularity_score(df: pd.DataFrame) -> pd.DataFrame:
        """
        Composite popularity score = 0.6 × rate_normalized + 0.4 × votes_normalized
        Both components scaled to [0, 1].
        Interpretability: high score = high rating AND high engagement.
        """
        df = df.copy()
        rate_norm  = df[Cols.RATE_NUMERIC].fillna(df[Cols.RATE_NUMERIC].median())
        votes_norm = df[Cols.VOTES]

        rate_scaled  = (rate_norm  - rate_norm.min())  / (rate_norm.max()  - rate_norm.min())
        votes_scaled = (votes_norm - votes_norm.min()) / (votes_norm.max() - votes_norm.min())

        df["popularity_score"] = (0.6 * rate_scaled + 0.4 * votes_scaled).round(4)
        logger.info(f"popularity_score: mean={df['popularity_score'].mean():.3f}, std={df['popularity_score'].std():.3f}")
        return df

    @staticmethod
    def add_value_for_money(df: pd.DataFrame) -> pd.DataFrame:
        """
        Value-for-money index = rate_numeric / log1p(approx_cost)
        Higher = better rating per rupee spent.
        """
        df = df.copy()
        rate = df[Cols.RATE_NUMERIC].fillna(df[Cols.RATE_NUMERIC].median())
        df["value_for_money"] = (rate / np.log1p(df[Cols.COST_CLEAN])).round(4)
        return df

    @staticmethod
    def add_cuisine_diversity(df: pd.DataFrame) -> pd.DataFrame:
        """
        Count of cuisines offered per restaurant.
        Already created in cleaning; this ensures it's always present.
        """
        df = df.copy()
        if "cuisine_count" not in df.columns:
            df["cuisine_count"] = (
                df[Cols.CUISINES].astype(str).str.split(",").apply(len)
            )
        return df

    @staticmethod
    def add_service_level(df: pd.DataFrame) -> pd.DataFrame:
        """
        Ordinal service_level based on online_order + book_table combination:
          0 = No online order, no booking
          1 = Online order only
          2 = Booking only
          3 = Full service (both)
        """
        df = df.copy()
        df["service_level"] = (
            df[Cols.ONLINE_ORDER].astype(int) +
            df[Cols.BOOK_TABLE].astype(int) * 2
        )
        return df

    @staticmethod
    def add_location_tier(df: pd.DataFrame) -> pd.DataFrame:
        """
        Tier classification based on average cost in the area:
          Tier-1: avg cost > 900 (premium zones)
          Tier-2: avg cost 500-900 (mid zones)
          Tier-3: avg cost < 500 (budget zones)
        """
        df = df.copy()
        avg_cost = df.groupby(Cols.LOCATION)[Cols.COST_CLEAN].transform("mean")
        df["location_tier"] = pd.cut(
            avg_cost,
            bins=[-1, 500, 900, float("inf")],
            labels=["Tier-3 Budget", "Tier-2 Mid", "Tier-1 Premium"],
        )
        return df

    @staticmethod
    def add_restaurant_segments(df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
        """
        KMeans clustering on [rate_numeric, approx_cost, votes] to find natural
        restaurant segments.
        Segment labels: Economy, Mainstream, Premium, Elite
        """
        df = df.copy()
        features = df[[Cols.RATE_NUMERIC, Cols.COST_CLEAN, Cols.VOTES]].copy()
        features = features.fillna(features.median())

        scaler = StandardScaler()
        scaled = scaler.fit_transform(features)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        df["segment_id"] = kmeans.fit_predict(scaled)

        # Label segments by mean cost
        seg_cost = df.groupby("segment_id")[Cols.COST_CLEAN].mean().sort_values()
        seg_labels = {
            seg_cost.index[0]: "Economy",
            seg_cost.index[1]: "Mainstream",
            seg_cost.index[2]: "Premium",
            seg_cost.index[3]: "Elite",
        }
        df["restaurant_segment"] = df["segment_id"].map(seg_labels)
        df = df.drop(columns=["segment_id"])

        logger.info(f"restaurant_segment distribution:\n{df['restaurant_segment'].value_counts()}")
        return df

    @classmethod
    def run_all(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all feature engineering transformations."""
        df = cls.add_popularity_score(df)
        df = cls.add_value_for_money(df)
        df = cls.add_cuisine_diversity(df)
        df = cls.add_service_level(df)
        df = cls.add_location_tier(df)
        df = cls.add_restaurant_segments(df)
        logger.info(f"Feature engineering complete → {df.shape[1]} total columns")
        return df


# ─────────────────────────────────────────────
# STATISTICAL PREPROCESSING
# ─────────────────────────────────────────────
class StatisticalPrep:
    """Encoding and scaling for statistical / ML analysis."""

    @staticmethod
    def encode_categoricals(df: pd.DataFrame, cols: List[str]) -> Tuple[pd.DataFrame, dict]:
        """Label-encode specified columns. Returns df and encoder dict."""
        df = df.copy()
        encoders = {}
        for col in cols:
            le = LabelEncoder()
            df[f"{col}_enc"] = le.fit_transform(df[col].astype(str).fillna("Unknown"))
            encoders[col] = le
        return df, encoders

    @staticmethod
    def normalize_numerics(df: pd.DataFrame, cols: List[str], method: str = "minmax") -> pd.DataFrame:
        """Normalize numeric columns using MinMax or Standard scaling."""
        df = df.copy()
        scaler = MinMaxScaler() if method == "minmax" else StandardScaler()
        df[[f"{c}_norm" for c in cols]] = scaler.fit_transform(df[cols].fillna(0))
        return df

    @staticmethod
    def build_ml_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare a feature matrix for ML experiments.
        Drops non-numeric / high-cardinality columns.
        """
        cat_cols = [Cols.ONLINE_ORDER, Cols.BOOK_TABLE, Cols.PRIMARY_REST_TYPE,
                    Cols.PRIMARY_CUISINE, Cols.LOCATION]
        df, _ = StatisticalPrep.encode_categoricals(df, cat_cols)

        feature_cols = [
            Cols.COST_CLEAN, Cols.VOTES, "cuisine_count", "service_level",
            f"{Cols.ONLINE_ORDER}_enc", f"{Cols.BOOK_TABLE}_enc",
            f"{Cols.PRIMARY_REST_TYPE}_enc", f"{Cols.PRIMARY_CUISINE}_enc",
            f"{Cols.LOCATION}_enc", "popularity_score", "value_for_money",
        ]
        ml_df = df[[c for c in feature_cols if c in df.columns]].copy()
        logger.info(f"ML feature matrix: {ml_df.shape}")
        return ml_df


# ─────────────────────────────────────────────
# DATA VALIDATOR
# ─────────────────────────────────────────────
class DataValidator:
    """
    Schema and constraint validation on the cleaned dataset.
    Raises AssertionError with descriptive messages if any constraint fails.
    Use in CI/CD or notebook QA cell.
    """

    EXPECTED_COLS = {
        Cols.NAME, Cols.ONLINE_ORDER, Cols.BOOK_TABLE,
        Cols.RATE_NUMERIC, Cols.VOTES, Cols.LOCATION,
        Cols.PRIMARY_REST_TYPE, Cols.PRIMARY_CUISINE,
        Cols.COST_CLEAN, Cols.COST_BUCKET, Cols.VOTES_BUCKET,
    }

    @classmethod
    def validate(cls, df: pd.DataFrame) -> bool:
        """Run all validation checks. Returns True if all pass."""
        cls._check_columns(df)
        cls._check_rate_range(df)
        cls._check_cost_positive(df)
        cls._check_votes_non_negative(df)
        cls._check_no_full_null_rows(df)
        cls._check_min_rows(df)
        logger.info("✅ All validation checks passed.")
        return True

    @classmethod
    def _check_columns(cls, df: pd.DataFrame):
        missing = cls.EXPECTED_COLS - set(df.columns)
        assert not missing, f"Missing expected columns: {missing}"

    @classmethod
    def _check_rate_range(cls, df: pd.DataFrame):
        valid = df[Cols.RATE_NUMERIC].dropna()
        assert valid.between(1.0, 5.0).all(), \
            f"rate_numeric out of [1,5] range. min={valid.min()}, max={valid.max()}"

    @classmethod
    def _check_cost_positive(cls, df: pd.DataFrame):
        assert (df[Cols.COST_CLEAN] > 0).all(), "approx_cost has non-positive values"

    @classmethod
    def _check_votes_non_negative(cls, df: pd.DataFrame):
        assert (df[Cols.VOTES] >= 0).all(), "votes column has negative values"

    @classmethod
    def _check_no_full_null_rows(cls, df: pd.DataFrame):
        full_null = df.isnull().all(axis=1).sum()
        assert full_null == 0, f"{full_null} rows are entirely null"

    @classmethod
    def _check_min_rows(cls, df: pd.DataFrame, min_rows: int = 40_000):
        assert len(df) >= min_rows, \
            f"Cleaned dataset has only {len(df):,} rows (expected ≥ {min_rows:,})"


# ─────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    from src.utils import load_cleaned_data
    df = load_cleaned_data()
    df = FeatureEngineer.run_all(df)
    DataValidator.validate(df)
    print(df[["popularity_score", "value_for_money", "restaurant_segment", "location_tier"]].describe())
