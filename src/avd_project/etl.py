from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from avd_project.config import PROCESSED_DATA_DIR, RAW_DATA_DIR


REQUIRED_COLUMNS = {
    "title",
    "price_gbp",
    "rating",
    "availability",
    "category",
    "product_url",
    "image_url",
}


def load_raw_books(path: str | Path | None = None) -> pd.DataFrame:
    source = Path(path) if path else RAW_DATA_DIR / "books_raw.csv"
    return pd.read_csv(source)


def validate_raw_books(df: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        columns = ", ".join(sorted(missing_columns))
        raise ValueError(f"Colunas obrigatorias ausentes: {columns}")


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    text_columns = ["title", "availability", "category", "product_url", "image_url"]
    cleaned = df.copy()

    for column in text_columns:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    return cleaned


def add_calculated_metrics(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()

    enriched["price_gbp"] = pd.to_numeric(enriched["price_gbp"], errors="coerce")
    enriched["rating"] = pd.to_numeric(enriched["rating"], errors="coerce")
    enriched = enriched.dropna(subset=["title", "price_gbp", "rating", "category"])
    enriched = enriched[enriched["price_gbp"] > 0]

    enriched["rating"] = enriched["rating"].astype("int64")
    enriched["is_available"] = enriched["availability"].str.contains(
        "in stock", case=False, na=False
    )
    enriched["title_length"] = enriched["title"].str.len()
    enriched["price_per_rating"] = enriched["price_gbp"] / enriched["rating"]
    enriched["value_score"] = enriched["rating"] / enriched["price_gbp"]

    category_mean = enriched.groupby("category")["price_gbp"].transform("mean")
    category_std = enriched.groupby("category")["price_gbp"].transform("std").replace(0, np.nan)
    enriched["price_vs_category_mean"] = enriched["price_gbp"] - category_mean
    enriched["category_price_zscore"] = (
        (enriched["price_gbp"] - category_mean) / category_std
    ).fillna(0)

    enriched["price_quartile"] = pd.qcut(
        enriched["price_gbp"],
        q=4,
        labels=["baixo", "medio-baixo", "medio-alto", "alto"],
        duplicates="drop",
    )
    enriched["rating_label"] = enriched["rating"].map(
        {
            1: "muito baixa",
            2: "baixa",
            3: "media",
            4: "alta",
            5: "excelente",
        }
    )

    return enriched


def transform_books(df: pd.DataFrame) -> pd.DataFrame:
    validate_raw_books(df)
    transformed = clean_text_columns(df)
    transformed = transformed.drop_duplicates(subset=["title", "category", "product_url"])
    transformed = add_calculated_metrics(transformed)

    ordered_columns = [
        "title",
        "category",
        "price_gbp",
        "rating",
        "rating_label",
        "availability",
        "is_available",
        "price_quartile",
        "title_length",
        "price_per_rating",
        "value_score",
        "price_vs_category_mean",
        "category_price_zscore",
        "product_url",
        "image_url",
    ]
    return transformed[ordered_columns].sort_values(["category", "title"]).reset_index(drop=True)


def save_processed_books(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination = Path(output_path) if output_path else PROCESSED_DATA_DIR / "books_processed.csv"
    df.to_csv(destination, index=False, encoding="utf-8")
    return destination


def run_etl(
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    raw_df = load_raw_books(input_path)
    processed_df = transform_books(raw_df)
    return save_processed_books(processed_df, output_path)
