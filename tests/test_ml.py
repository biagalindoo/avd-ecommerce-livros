import pandas as pd

from avd_project.ml import ml_segment_summary, segment_books


def sample_books():
    return pd.DataFrame(
        [
            {"title": "A", "price_gbp": 10.0, "rating": 5, "value_score": 0.5, "title_length": 1},
            {"title": "B", "price_gbp": 12.0, "rating": 4, "value_score": 0.33, "title_length": 1},
            {"title": "C", "price_gbp": 55.0, "rating": 5, "value_score": 0.09, "title_length": 1},
            {"title": "D", "price_gbp": 50.0, "rating": 4, "value_score": 0.08, "title_length": 1},
            {"title": "E", "price_gbp": 35.0, "rating": 2, "value_score": 0.06, "title_length": 1},
            {"title": "F", "price_gbp": 30.0, "rating": 1, "value_score": 0.03, "title_length": 1},
        ]
    )


def test_segment_books_adds_ml_columns():
    result = segment_books(sample_books())

    assert "ml_cluster" in result.columns
    assert "ml_segment" in result.columns
    assert result["ml_segment"].nunique() == 3


def test_ml_segment_summary_returns_profiles():
    result = ml_segment_summary(sample_books())

    assert {"ml_segment", "books_count", "avg_price_gbp", "avg_rating"}.issubset(result.columns)
    assert len(result) == 3
