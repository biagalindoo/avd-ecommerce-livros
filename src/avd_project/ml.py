from __future__ import annotations

from pathlib import Path
import os

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from avd_project.config import PROCESSED_DATA_DIR


FEATURE_COLUMNS = ["price_gbp", "rating", "value_score", "title_length"]

SEGMENT_LABELS = {
    0: "Oferta equilibrada",
    1: "Premium de alta nota",
    2: "Economico bem avaliado",
}

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "2")


def load_processed_books(path: str | Path | None = None) -> pd.DataFrame:
    source = Path(path) if path else PROCESSED_DATA_DIR / "books_processed.csv"
    return pd.read_csv(source)


def segment_books(df: pd.DataFrame, clusters: int = 3, random_state: int = 42) -> pd.DataFrame:
    available_columns = [column for column in FEATURE_COLUMNS if column in df.columns]
    if len(available_columns) < 2:
        raise ValueError("Dados insuficientes para segmentacao com Machine Learning.")

    segmented = df.copy()
    features = segmented[available_columns].fillna(segmented[available_columns].median())
    scaled_features = StandardScaler().fit_transform(features)

    model = KMeans(n_clusters=clusters, random_state=random_state, n_init=10)
    segmented["ml_cluster"] = model.fit_predict(scaled_features)

    cluster_profiles = (
        segmented.groupby("ml_cluster")
        .agg(
            avg_price=("price_gbp", "mean"),
            avg_rating=("rating", "mean"),
            avg_value=("value_score", "mean"),
        )
        .sort_values(["avg_value", "avg_rating"], ascending=False)
        .reset_index()
    )
    label_by_cluster = {
        row.ml_cluster: SEGMENT_LABELS.get(index, f"Segmento {index + 1}")
        for index, row in cluster_profiles.iterrows()
    }
    segmented["ml_segment"] = segmented["ml_cluster"].map(label_by_cluster)
    return segmented


def ml_segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    segmented = segment_books(df)
    return (
        segmented.groupby("ml_segment", as_index=False)
        .agg(
            books_count=("title", "count"),
            avg_price_gbp=("price_gbp", "mean"),
            avg_rating=("rating", "mean"),
            avg_value_score=("value_score", "mean"),
        )
        .sort_values("avg_value_score", ascending=False)
        .reset_index(drop=True)
    )
