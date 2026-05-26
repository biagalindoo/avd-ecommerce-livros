from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from avd_project.analysis import category_summary
from avd_project.config import PROCESSED_DATA_DIR, PROJECT_ROOT


EXPORTS_DIR = PROJECT_ROOT / "exports" / "figures"

COLOR_PRIMARY = "#2563eb"
COLOR_ACCENT = "#f97316"
COLOR_MUTED = "#94a3b8"
COLOR_GOOD = "#16a34a"
COLOR_BG = "#ffffff"
COLOR_TEXT = "#1f2937"


def load_processed_books(path: str | Path | None = None) -> pd.DataFrame:
    source = Path(path) if path else PROCESSED_DATA_DIR / "books_processed.csv"
    return pd.read_csv(source)


def apply_story_layout(fig: go.Figure, title: str, subtitle: str = "") -> go.Figure:
    full_title = f"{title}<br><sup>{subtitle}</sup>" if subtitle else title
    fig.update_layout(
        title={
            "text": full_title,
            "x": 0.02,
            "xanchor": "left",
        },
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font={"family": "Arial", "color": COLOR_TEXT, "size": 13},
        margin={"l": 48, "r": 24, "t": 88, "b": 48},
        hoverlabel={"bgcolor": "white", "font_size": 12},
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#e5e7eb", zeroline=False)
    return fig


def plot_category_opportunities(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    summary = category_summary(df).head(top_n).copy()
    summary = summary.sort_values("avg_value_score")

    fig = px.bar(
        summary,
        x="avg_value_score",
        y="category",
        orientation="h",
        color="avg_rating",
        color_continuous_scale=["#cbd5e1", COLOR_PRIMARY, COLOR_GOOD],
        labels={
            "avg_value_score": "Pontuacao de valor media",
            "category": "Categoria",
            "avg_rating": "Nota media",
        },
        hover_data={
            "books_count": True,
            "avg_price_gbp": ":.2f",
            "avg_rating": ":.2f",
            "avg_value_score": ":.3f",
        },
    )
    fig.update_traces(marker_line_width=0, opacity=0.95)
    return apply_story_layout(
        fig,
        "Categorias com melhor equilibrio entre nota e preco",
        "Barras maiores indicam categorias com maior nota por libra gasta.",
    )


def plot_price_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df,
        x="price_gbp",
        nbins=28,
        color_discrete_sequence=[COLOR_PRIMARY],
        labels={"price_gbp": "Preco em libra", "count": "Quantidade de livros"},
    )

    median_price = df["price_gbp"].median()
    fig.add_vline(
        x=median_price,
        line_width=3,
        line_dash="dash",
        line_color=COLOR_ACCENT,
        annotation_text=f"Mediana: GBP {median_price:.2f}",
        annotation_position="top right",
    )
    fig.update_traces(marker_line_width=0, opacity=0.82)
    return apply_story_layout(
        fig,
        "Distribuicao de precos do catalogo",
        "A linha laranja cria contraste e guia a leitura para o preco central.",
    )


def plot_rating_price_scatter(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df,
        x="price_gbp",
        y="rating",
        color="price_quartile",
        size="value_score",
        hover_name="title",
        hover_data={"category": True, "price_gbp": ":.2f", "value_score": ":.3f"},
        color_discrete_map={
            "baixo": COLOR_GOOD,
            "medio-baixo": COLOR_PRIMARY,
            "medio-alto": COLOR_MUTED,
            "alto": COLOR_ACCENT,
        },
        labels={
            "price_gbp": "Preco em libra",
            "rating": "Nota",
            "price_quartile": "Faixa de preco",
            "value_score": "Valor",
        },
    )
    fig.update_traces(marker={"line": {"width": 0}, "opacity": 0.72})
    fig.update_yaxes(dtick=1)
    return apply_story_layout(
        fig,
        "Preco e avaliacao nao caminham sempre juntos",
        "Agrupamento por faixa de preco ajuda a perceber excecoes e oportunidades.",
    )


def plot_top_value_books(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    top_books = df.nlargest(top_n, "value_score").sort_values("value_score")

    fig = px.bar(
        top_books,
        x="value_score",
        y="title",
        orientation="h",
        color="rating",
        color_continuous_scale=["#cbd5e1", COLOR_PRIMARY, COLOR_GOOD],
        labels={
            "value_score": "Nota por libra",
            "title": "Livro",
            "rating": "Nota",
        },
        hover_data={"category": True, "price_gbp": ":.2f", "rating": True},
    )
    fig.update_traces(marker_line_width=0)
    fig.update_yaxes(tickfont={"size": 10})
    return apply_story_layout(
        fig,
        "Livros com maior valor percebido",
        "A ordenacao horizontal reduz esforco de comparacao e evidencia o topo do ranking.",
    )


def build_figures(df: pd.DataFrame) -> dict[str, go.Figure]:
    return {
        "category_opportunities": plot_category_opportunities(df),
        "price_distribution": plot_price_distribution(df),
        "rating_price_scatter": plot_rating_price_scatter(df),
        "top_value_books": plot_top_value_books(df),
    }


def save_figures(
    df: pd.DataFrame,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    destination = Path(output_dir) if output_dir else EXPORTS_DIR
    destination.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, Path] = {}
    for name, fig in build_figures(df).items():
        path = destination / f"{name}.html"
        fig.write_html(path, include_plotlyjs="cdn", full_html=True)
        outputs[name] = path

    return outputs


def run_visualizations(
    input_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    df = load_processed_books(input_path)
    return save_figures(df, output_dir)
