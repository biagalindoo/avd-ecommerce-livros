from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from avd_project.analysis import (  # noqa: E402
    category_anova,
    category_summary,
    detect_price_outliers,
    pearson_correlations,
)
from avd_project.config import PROCESSED_DATA_DIR  # noqa: E402
from avd_project.visualization import (  # noqa: E402
    plot_category_opportunities,
    plot_price_distribution,
    plot_rating_price_scatter,
    plot_top_value_books,
)


st.set_page_config(
    page_title="AVD - Ecommerce de Livros",
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_custom_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --avd-bg: #f8fafc;
            --avd-panel: #ffffff;
            --avd-text: #111827;
            --avd-muted: #374151;
            --avd-border: #d1d5db;
            --avd-accent: #dc2626;
        }

        .stApp {
            background: var(--avd-bg);
            color: var(--avd-text);
        }

        section[data-testid="stSidebar"] {
            background: #111827;
            border-right: 1px solid #374151;
        }

        section[data-testid="stSidebar"] * {
            color: #f9fafb !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="select"] span,
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
            color: #f9fafb !important;
        }

        div[data-baseweb="select"] input,
        div[data-baseweb="select"] span {
            color: #f9fafb !important;
        }

        .block-container {
            padding: 3rem 2rem 4rem 2rem;
            max-width: 1480px;
        }

        h1, h2, h3, h4, h5, h6, p, label, span, div {
            color: var(--avd-text);
        }

        [data-testid="stCaptionContainer"] p {
            color: var(--avd-muted);
            font-size: 1rem;
        }

        [data-testid="stMetric"] {
            background: var(--avd-panel);
            border: 1px solid var(--avd-border);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
        }

        [data-testid="stMetricLabel"] p {
            color: #4b5563;
            font-weight: 700;
        }

        [data-testid="stMetricValue"] {
            color: #111827;
            font-weight: 800;
        }

        .stPlotlyChart {
            background: #ffffff;
            border: 1px solid var(--avd-border);
            border-radius: 8px;
            padding: 0.7rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
        }

        .stPlotlyChart svg text {
            fill: #111827 !important;
            color: #111827 !important;
            opacity: 1 !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            border-bottom: 1px solid var(--avd-border);
        }

        .stTabs [data-baseweb="tab"] {
            color: #374151;
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            color: var(--avd-accent);
        }

        .stDataFrame {
            background: #ffffff;
            border: 1px solid var(--avd-border);
            border-radius: 8px;
            padding: 0.4rem;
        }

        .insight-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1.1rem 0 1.4rem 0;
        }

        .insight-card {
            background: #ffffff;
            border: 1px solid var(--avd-border);
            border-left: 5px solid var(--avd-accent);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
        }

        .insight-card strong {
            color: #111827;
            display: block;
            font-size: 0.95rem;
            margin-bottom: 0.35rem;
        }

        .insight-card span {
            color: #374151;
            font-size: 0.92rem;
            line-height: 1.35;
        }

        @media (max-width: 900px) {
            .insight-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_books() -> pd.DataFrame:
    data_path = PROCESSED_DATA_DIR / "books_processed.csv"
    if not data_path.exists():
        return pd.DataFrame()
    return pd.read_csv(data_path)


def format_gbp(value: float) -> str:
    return f"GBP {value:,.2f}"


def filter_books(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")

    categories = sorted(df["category"].dropna().unique())
    selected_categories = st.sidebar.multiselect(
        "Categorias",
        options=categories,
        default=[],
        placeholder="Todas as categorias",
        help="Deixe vazio para considerar todas as categorias.",
    )

    min_price = float(df["price_gbp"].min())
    max_price = float(df["price_gbp"].max())
    selected_price = st.sidebar.slider(
        "Faixa de preco (GBP)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=0.5,
    )

    selected_ratings = st.sidebar.multiselect(
        "Notas",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
    )

    only_available = st.sidebar.checkbox("Somente disponiveis", value=True)

    filtered = df[
        df["rating"].isin(selected_ratings)
        & df["price_gbp"].between(selected_price[0], selected_price[1])
    ].copy()

    if selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]

    if only_available:
        filtered = filtered[filtered["is_available"]]

    return filtered


def render_empty_state() -> None:
    st.title("Ecommerce de Livros")
    st.info(
        "Os dados processados ainda nao foram encontrados. Rode primeiro "
        "`python scripts/run_scraping.py` e depois `python scripts/run_etl.py`."
    )


def render_kpis(df: pd.DataFrame) -> None:
    books_count = len(df)
    categories_count = df["category"].nunique()
    avg_price = df["price_gbp"].mean()
    avg_rating = df["rating"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Livros analisados", f"{books_count:,}".replace(",", "."))
    col2.metric("Categorias", categories_count)
    col3.metric("Preco medio", format_gbp(avg_price))
    col4.metric("Nota media", f"{avg_rating:.2f}/5")


def render_insights(df: pd.DataFrame) -> None:
    summary = category_summary(df)
    best_category = summary.sort_values("avg_value_score", ascending=False).iloc[0]
    best_book = df.sort_values("value_score", ascending=False).iloc[0]
    median_price = df["price_gbp"].median()

    st.markdown(
        f"""
        <div class="insight-grid">
            <div class="insight-card">
                <strong>Categoria mais eficiente</strong>
                <span>{best_category["category"]} combina nota media de
                {best_category["avg_rating"]:.2f} com melhor valor relativo.</span>
            </div>
            <div class="insight-card">
                <strong>Livro com maior valor percebido</strong>
                <span>{best_book["title"]} tem nota {int(best_book["rating"])}
                e preco de {format_gbp(best_book["price_gbp"])}.</span>
            </div>
            <div class="insight-card">
                <strong>Preco central do catalogo</strong>
                <span>A mediana esta em {format_gbp(median_price)}, melhor
                referencia que a media quando ha valores extremos.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_tab(df: pd.DataFrame) -> None:
    left, right = st.columns([1.1, 1])
    with left:
        st.plotly_chart(plot_price_distribution(df), use_container_width=True, theme=None)
    with right:
        st.plotly_chart(plot_rating_price_scatter(df), use_container_width=True, theme=None)


def render_opportunities_tab(df: pd.DataFrame) -> None:
    st.plotly_chart(plot_category_opportunities(df), use_container_width=True, theme=None)
    st.plotly_chart(plot_top_value_books(df), use_container_width=True, theme=None)


def render_statistics_tab(df: pd.DataFrame) -> None:
    summary = category_summary(df)
    correlations = pearson_correlations(df)
    anova = category_anova(df)
    outliers = detect_price_outliers(df)

    st.subheader("Resumo por categoria")
    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "avg_price_gbp": st.column_config.NumberColumn("Preco medio", format="GBP %.2f"),
            "median_price_gbp": st.column_config.NumberColumn("Mediana", format="GBP %.2f"),
            "avg_rating": st.column_config.NumberColumn("Nota media", format="%.2f"),
            "availability_rate": st.column_config.ProgressColumn(
                "Disponibilidade",
                min_value=0,
                max_value=1,
                format="%.0f%%",
            ),
        },
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Correlacao de Pearson")
        st.dataframe(correlations, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("ANOVA")
        st.dataframe(anova, use_container_width=True, hide_index=True)

    st.subheader("Outliers de preco")
    st.dataframe(outliers, use_container_width=True, hide_index=True)


def render_data_tab(df: pd.DataFrame) -> None:
    search = st.text_input("Buscar livro pelo titulo")
    table = df.copy()
    if search:
        table = table[table["title"].str.contains(search, case=False, na=False)]

    st.dataframe(
        table[
            [
                "title",
                "category",
                "price_gbp",
                "rating",
                "rating_label",
                "value_score",
                "product_url",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "product_url": st.column_config.LinkColumn("Pagina do produto"),
            "price_gbp": st.column_config.NumberColumn("Preco", format="GBP %.2f"),
            "value_score": st.column_config.NumberColumn("Valor", format="%.3f"),
        },
    )


def main() -> None:
    apply_custom_theme()

    df = load_books()
    if df.empty:
        render_empty_state()
        return

    st.title("Ecommerce de Livros")
    st.caption(
        "Dashboard interativo para analisar preco, avaliacao e oportunidades "
        "com dados obtidos por web scraping."
    )

    filtered = filter_books(df)
    if filtered.empty:
        st.warning("Nenhum livro encontrado com os filtros selecionados.")
        return

    render_kpis(filtered)
    render_insights(filtered)

    overview_tab, opportunities_tab, statistics_tab, data_tab = st.tabs(
        ["Visao geral", "Oportunidades", "Estatistica", "Dados"]
    )
    with overview_tab:
        render_overview_tab(filtered)
    with opportunities_tab:
        render_opportunities_tab(filtered)
    with statistics_tab:
        render_statistics_tab(filtered)
    with data_tab:
        render_data_tab(filtered)


if __name__ == "__main__":
    main()
