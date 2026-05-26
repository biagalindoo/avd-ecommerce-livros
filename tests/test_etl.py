import pandas as pd

from avd_project.etl import transform_books


def test_transform_books_cleans_and_enriches_data():
    raw_df = pd.DataFrame(
        [
            {
                "title": "  Livro A  ",
                "price_gbp": "10.00",
                "rating": "5",
                "availability": " In stock ",
                "category": " Fiction ",
                "product_url": "https://example.com/a",
                "image_url": "https://example.com/a.jpg",
            },
            {
                "title": "Livro A",
                "price_gbp": "10.00",
                "rating": "5",
                "availability": "In stock",
                "category": "Fiction",
                "product_url": "https://example.com/a",
                "image_url": "https://example.com/a.jpg",
            },
            {
                "title": "Livro B",
                "price_gbp": "20.00",
                "rating": "2",
                "availability": "In stock",
                "category": "Fiction",
                "product_url": "https://example.com/b",
                "image_url": "https://example.com/b.jpg",
            },
        ]
    )

    result = transform_books(raw_df)

    assert len(result) == 2
    assert result.loc[0, "title"] == "Livro A"
    assert result.loc[0, "is_available"]
    assert result.loc[0, "rating_label"] == "excelente"
    assert "value_score" in result.columns
    assert "category_price_zscore" in result.columns
