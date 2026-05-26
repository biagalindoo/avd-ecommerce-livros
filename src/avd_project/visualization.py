from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from avd_project.analysis import category_summary
from avd_project.config import PROCESSED_DATA_DIR, PROJECT_ROOT
from avd_project.ml import segment_books


EXPORTS_DIR = PROJECT_ROOT / "exports" / "figures"

COLOR_PRIMARY = "#2563eb"
COLOR_ACCENT = "#f97316"
COLOR_MUTED = "#94a3b8"
COLOR_GOOD = "#16a34a"
COLOR_BG = "#ffffff"
COLOR_TEXT = "#111827"
COLOR_AXIS = "#374151"
COLOR_GRID = "#d1d5db"


def shorten_label(value: str, max_length: int = 34) -> str:
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 3].rstrip()}..."


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
            "font": {"size": 20, "color": COLOR_TEXT},
        },
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        template="plotly_white",
        font={"family": "Arial", "color": COLOR_TEXT, "size": 14},
        margin={"l": 56, "r": 28, "t": 96, "b": 56},
        hoverlabel={"bgcolor": "white", "font_size": 13, "font_color": COLOR_TEXT},
        legend_title_text="",
        legend={"font": {"color": COLOR_TEXT, "size": 12}},
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        color=COLOR_AXIS,
        title_font={"color": COLOR_AXIS, "size": 14},
        tickfont={"color": COLOR_AXIS, "size": 12},
    )
    fig.update_yaxes(
        gridcolor=COLOR_GRID,
        zeroline=False,
        color=COLOR_AXIS,
        title_font={"color": COLOR_AXIS, "size": 14},
        tickfont={"color": COLOR_AXIS, "size": 12},
    )
    return fig


def apply_bar_story_layout(
    fig: go.Figure,
    title: str,
    subtitle: str = "",
    left_margin: int = 56,
    height: int | None = None,
) -> go.Figure:
    fig = apply_story_layout(fig, title, subtitle)
    fig.update_layout(margin={"l": left_margin, "r": 36, "t": 96, "b": 64})
    if height is not None:
        fig.update_layout(height=height)
    fig.update_yaxes(title_text="", automargin=True)
    fig.update_layout(yaxis_title="")
    return fig


def plot_category_opportunities(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    summary = category_summary(df).head(top_n).copy()
    summary = summary.sort_values("avg_value_score")
    summary = summary.assign(
        category_short=summary["category"].map(lambda category: shorten_label(str(category), 22))
    )

    fig = px.bar(
        summary,
        x="avg_value_score",
        y="category_short",
        orientation="h",
        color="avg_rating",
        color_continuous_scale=["#cbd5e1", COLOR_PRIMARY, COLOR_GOOD],
        labels={
            "avg_value_score": "Pontuacao de valor media",
            "category_short": "",
            "avg_rating": "Nota media",
        },
        custom_data=["category", "books_count", "avg_price_gbp", "avg_rating"],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Livros: %{customdata[1]}<br>"
            "Preco medio: GBP %{customdata[2]:.2f}<br>"
            "Nota media: %{customdata[3]:.2f}<br>"
            "Valor medio: %{x:.3f}<extra></extra>"
        ),
        marker_line_width=0,
        opacity=0.95,
    )
    return apply_bar_story_layout(
        fig,
        "Categorias: nota x preco",
        "Barras maiores indicam mais nota por libra gasta.",
        left_margin=190,
        height=620,
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
        "Distribuicao de precos",
        "A linha laranja marca o preco central.",
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
        "Preco x avaliacao",
        "As cores separam as faixas de preco.",
    )


def plot_top_value_books(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    top_books = df.nlargest(top_n, "value_score").sort_values("value_score")
    top_books = top_books.assign(
        title_short=top_books["title"].map(lambda title: shorten_label(str(title), 30))
    )

    fig = px.bar(
        top_books,
        x="value_score",
        y="title_short",
        orientation="h",
        color="rating",
        color_continuous_scale=["#cbd5e1", COLOR_PRIMARY, COLOR_GOOD],
        labels={
            "value_score": "Nota por libra",
            "title_short": "",
            "rating": "Nota",
        },
        custom_data=["title", "category", "price_gbp", "rating"],
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Categoria: %{customdata[1]}<br>"
            "Preco: GBP %{customdata[2]:.2f}<br>"
            "Nota: %{customdata[3]}<br>"
            "Nota por libra: %{x:.3f}<extra></extra>"
        ),
        marker_line_width=0,
    )
    fig.update_yaxes(tickfont={"size": 12})
    return apply_bar_story_layout(
        fig,
        "Top livros por valor",
        "Ranking pela relacao entre nota e preco.",
        left_margin=230,
        height=640,
    )


def plot_ml_segments(df: pd.DataFrame) -> go.Figure:
    segmented = segment_books(df)
    fig = px.scatter(
        segmented,
        x="price_gbp",
        y="value_score",
        color="ml_segment",
        size="rating",
        hover_name="title",
        hover_data={"category": True, "price_gbp": ":.2f", "rating": True},
        labels={
            "price_gbp": "Preco em libra",
            "value_score": "Nota por libra",
            "ml_segment": "Segmento ML",
            "rating": "Nota",
        },
        color_discrete_sequence=[COLOR_GOOD, COLOR_PRIMARY, COLOR_ACCENT],
    )
    fig.update_traces(marker={"opacity": 0.72, "line": {"width": 0}})
    return apply_story_layout(
        fig,
        "Segmentacao por Machine Learning",
        "K-Means agrupa livros por preco, nota, valor e tamanho do titulo.",
    )


def build_figures(df: pd.DataFrame) -> dict[str, go.Figure]:
    return {
        "category_opportunities": plot_category_opportunities(df),
        "price_distribution": plot_price_distribution(df),
        "rating_price_scatter": plot_rating_price_scatter(df),
        "top_value_books": plot_top_value_books(df),
        "ml_segments": plot_ml_segments(df),
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
