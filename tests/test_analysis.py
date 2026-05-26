import pandas as pd

from avd_project.analysis import (
    category_anova,
    category_summary,
    detect_price_outliers,
    pearson_correlations,
    price_quartiles,
)


def sample_processed_books():
    return pd.DataFrame(
        [
            {
                "title": "A",
                "category": "Fiction",
                "price_gbp": 10.0,
                "rating": 5,
                "is_available": True,
                "title_length": 1,
                "price_per_rating": 2.0,
                "value_score": 0.5,
                "price_vs_category_mean": -10.0,
                "category_price_zscore": -0.7,
            },
            {
                "title": "B",
                "category": "Fiction",
                "price_gbp": 20.0,
                "rating": 4,
                "is_available": True,
                "title_length": 2,
                "price_per_rating": 5.0,
                "value_score": 0.2,
                "price_vs_category_mean": 0.0,
                "category_price_zscore": 0.0,
            },
            {
                "title": "C",
                "category": "Travel",
                "price_gbp": 30.0,
                "rating": 3,
                "is_available": False,
                "title_length": 3,
                "price_per_rating": 10.0,
                "value_score": 0.1,
                "price_vs_category_mean": 0.0,
                "category_price_zscore": 0.0,
            },
            {
                "title": "D",
                "category": "Travel",
                "price_gbp": 200.0,
                "rating": 1,
                "is_available": True,
                "title_length": 4,
                "price_per_rating": 200.0,
                "value_score": 0.005,
                "price_vs_category_mean": 170.0,
                "category_price_zscore": 1.5,
            },
        ]
    )


def test_price_quartiles_returns_expected_labels():
    result = price_quartiles(sample_processed_books())

    assert list(result["index"]) == ["q1", "median", "q3"]


def test_detect_price_outliers_marks_extreme_prices():
    result = detect_price_outliers(sample_processed_books())

    assert result.iloc[0]["title"] == "D"


def test_pearson_correlations_returns_required_pairs():
    result = pearson_correlations(sample_processed_books())

    assert len(result) == 3
    assert {"variable_a", "variable_b", "pearson_r", "p_value"}.issubset(result.columns)


def test_category_anova_returns_one_row():
    result = category_anova(sample_processed_books())

    assert result.loc[0, "test"] == "anova_price_by_category"
    assert result.loc[0, "groups"] == 2


def test_category_summary_groups_by_category():
    result = category_summary(sample_processed_books())

    assert set(result["category"]) == {"Fiction", "Travel"}
    assert "avg_price_gbp" in result.columns
