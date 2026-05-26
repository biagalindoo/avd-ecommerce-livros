import pandas as pd
import pytest

pytest.importorskip("plotly")
from avd_project.visualization import build_figures


def sample_processed_books():
    return pd.DataFrame(
        [
            {
                "title": "Livro A",
                "category": "Fiction",
                "price_gbp": 10.0,
                "rating": 5,
                "rating_label": "excelente",
                "availability": "In stock",
                "is_available": True,
                "price_quartile": "baixo",
                "title_length": 7,
                "price_per_rating": 2.0,
                "value_score": 0.5,
                "price_vs_category_mean": -5.0,
                "category_price_zscore": -0.7,
                "product_url": "https://example.com/a",
                "image_url": "https://example.com/a.jpg",
            },
            {
                "title": "Livro B",
                "category": "Travel",
                "price_gbp": 40.0,
                "rating": 4,
                "rating_label": "alta",
                "availability": "In stock",
                "is_available": True,
                "price_quartile": "alto",
                "title_length": 7,
                "price_per_rating": 10.0,
                "value_score": 0.1,
                "price_vs_category_mean": 8.0,
                "category_price_zscore": 0.8,
                "product_url": "https://example.com/b",
                "image_url": "https://example.com/b.jpg",
            },
            {
                "title": "Livro C",
                "category": "Fiction",
                "price_gbp": 22.0,
                "rating": 3,
                "rating_label": "media",
                "availability": "In stock",
                "is_available": True,
                "price_quartile": "medio-baixo",
                "title_length": 7,
                "price_per_rating": 7.33,
                "value_score": 0.136,
                "price_vs_category_mean": 2.0,
                "category_price_zscore": 0.4,
                "product_url": "https://example.com/c",
                "image_url": "https://example.com/c.jpg",
            },
        ]
    )


def test_build_figures_returns_expected_story_charts():
    figures = build_figures(sample_processed_books())

    assert set(figures) == {
        "category_opportunities",
        "ml_segments",
        "price_distribution",
        "rating_price_scatter",
        "top_value_books",
    }
    for figure in figures.values():
        assert figure.layout.title.text
        assert figure.data
