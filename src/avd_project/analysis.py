from __future__ import annotations

from pathlib import Path

import pandas as pd

from avd_project.config import PROCESSED_DATA_DIR


NUMERIC_COLUMNS = [
    "price_gbp",
    "rating",
    "title_length",
    "price_per_rating",
    "value_score",
    "price_vs_category_mean",
    "category_price_zscore",
]


try:
    from scipy import stats
except ModuleNotFoundError:
    stats = None


def load_processed_books(path: str | Path | None = None) -> pd.DataFrame:
    source = Path(path) if path else PROCESSED_DATA_DIR / "books_processed.csv"
    return pd.read_csv(source)


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    available_columns = [column for column in NUMERIC_COLUMNS if column in df.columns]
    return df[available_columns].describe().T.reset_index(names="metric")


def price_quartiles(df: pd.DataFrame) -> pd.DataFrame:
    quartiles = df["price_gbp"].quantile([0.25, 0.5, 0.75]).rename(
        index={0.25: "q1", 0.5: "median", 0.75: "q3"}
    )
    return quartiles.reset_index(name="price_gbp")


def detect_price_outliers(df: pd.DataFrame) -> pd.DataFrame:
    q1 = df["price_gbp"].quantile(0.25)
    q3 = df["price_gbp"].quantile(0.75)
    iqr = q3 - q1
    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    outliers = df[(df["price_gbp"] < lower_limit) | (df["price_gbp"] > upper_limit)].copy()
    outliers["outlier_limit_low"] = lower_limit
    outliers["outlier_limit_high"] = upper_limit
    return outliers.sort_values("price_gbp", ascending=False).reset_index(drop=True)


def pearson_correlations(df: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("price_gbp", "rating"),
        ("price_gbp", "title_length"),
        ("rating", "value_score"),
    ]
    rows = []

    for column_a, column_b in pairs:
        valid = df[[column_a, column_b]].dropna()
        if len(valid) < 2:
            correlation = float("nan")
            p_value = float("nan")
        elif stats is None:
            correlation = valid[column_a].corr(valid[column_b], method="pearson")
            p_value = float("nan")
        else:
            correlation, p_value = stats.pearsonr(valid[column_a], valid[column_b])
        rows.append(
            {
                "variable_a": column_a,
                "variable_b": column_b,
                "pearson_r": correlation,
                "p_value": p_value,
            }
        )

    return pd.DataFrame(rows)


def category_anova(df: pd.DataFrame) -> pd.DataFrame:
    category_groups = [
        group["price_gbp"].dropna()
        for _, group in df.groupby("category")
        if len(group["price_gbp"].dropna()) >= 2
    ]

    if len(category_groups) < 2:
        statistic = float("nan")
        p_value = float("nan")
    elif stats is not None:
        statistic, p_value = stats.f_oneway(*category_groups)
    else:
        all_values = pd.concat(category_groups)
        overall_mean = all_values.mean()
        between_sum = sum(
            len(group) * (group.mean() - overall_mean) ** 2 for group in category_groups
        )
        within_sum = sum(((group - group.mean()) ** 2).sum() for group in category_groups)
        df_between = len(category_groups) - 1
        df_within = len(all_values) - len(category_groups)
        statistic = (between_sum / df_between) / (within_sum / df_within)
        p_value = float("nan")

    return pd.DataFrame(
        [
            {
                "test": "anova_price_by_category",
                "statistic": statistic,
                "p_value": p_value,
                "groups": len(category_groups),
            }
        ]
    )


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category", as_index=False)
        .agg(
            books_count=("title", "count"),
            avg_price_gbp=("price_gbp", "mean"),
            median_price_gbp=("price_gbp", "median"),
            avg_rating=("rating", "mean"),
            availability_rate=("is_available", "mean"),
            avg_value_score=("value_score", "mean"),
        )
        .sort_values(["books_count", "avg_rating"], ascending=[False, False])
        .reset_index(drop=True)
    )


def save_analysis_outputs(
    df: pd.DataFrame,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    destination = Path(output_dir) if output_dir else PROCESSED_DATA_DIR / "analysis"
    destination.mkdir(parents=True, exist_ok=True)

    outputs = {
        "descriptive_statistics": destination / "descriptive_statistics.csv",
        "price_quartiles": destination / "price_quartiles.csv",
        "price_outliers": destination / "price_outliers.csv",
        "pearson_correlations": destination / "pearson_correlations.csv",
        "category_anova": destination / "category_anova.csv",
        "category_summary": destination / "category_summary.csv",
    }

    descriptive_statistics(df).to_csv(outputs["descriptive_statistics"], index=False)
    price_quartiles(df).to_csv(outputs["price_quartiles"], index=False)
    detect_price_outliers(df).to_csv(outputs["price_outliers"], index=False)
    pearson_correlations(df).to_csv(outputs["pearson_correlations"], index=False)
    category_anova(df).to_csv(outputs["category_anova"], index=False)
    category_summary(df).to_csv(outputs["category_summary"], index=False)

    return outputs


def run_analysis(
    input_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    df = load_processed_books(input_path)
    return save_analysis_outputs(df, output_dir)
