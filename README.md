# Projeto Final - Análise e Visualização de Dados

Este projeto apresenta um pipeline completo de ciência de dados aplicado a um catálogo de livros em um ambiente de e-commerce. Os dados são obtidos por web scraping do site público [Books to Scrape](https://books.toscrape.com/) e processados até chegar a análises, visualizações e um dashboard interativo.

## O que o projeto faz

- Extrai dados de livros por meio de web scraping.
- Limpa e transforma os dados com `pandas`.
- Calcula métricas e estatísticas exploratórias.
- Gera visualizações analíticas em HTML.
- Oferece um dashboard interativo em `Streamlit`.
- Inclui uma análise de segmentação com K-Means para apoio à tomada de decisão.

## Estrutura do projeto

- `app/` — dashboard Streamlit.
- `data/raw/` — dados brutos coletados.
- `data/processed/` — dados limpos e prontos para análise.
- `notebooks/` — notebooks de exploração e validação.
- `scripts/` — scripts para executar scraping, ETL, análise e visualização.
- `src/avd_project/` — código fonte principal do projeto.
- `tests/` — testes automatizados.
- `requirements.txt` — dependências do projeto.

## Como usar

1. Crie o ambiente virtual:

```bash
python -m venv .venv
```

2. Ative o ambiente:

```bash
# Windows
.venv\Scripts\Activate.ps1
# ou
.venv\Scripts\activate.bat
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
pip install -e .
```

4. Execute as etapas do pipeline:

```bash
python scripts/run_scraping.py
python scripts/run_etl.py
python scripts/run_analysis.py
python scripts/run_visualizations.py
```

5. Inicie o dashboard:

```bash
streamlit run app/streamlit_app.py
```

## Principais scripts

- `scripts/run_scraping.py`: coleta os dados de livros.
- `scripts/run_etl.py`: transforma e normaliza os dados.
- `scripts/run_analysis.py`: calcula estatísticas e métricas.
- `scripts/run_visualizations.py`: gera gráficos e relatórios HTML.
- `app/streamlit_app.py`: dashboard interativo.

## Destaques do projeto

- Uso de `pandas` para tratamento e análise de dados.
- Visualizações baseadas em princípios de Gestalt.
- Dashboard Streamlit para exploração interativa.
- Segmentação de livros por K-Means usando variáveis como preço, avaliação, valor percebido e tamanho do título.
- Saídas com arquivos HTML e relatórios estruturados.

## Requisitos

- Python 3.10+ (recomendado)
- `pandas`
- `streamlit`
- `scikit-learn`
- `matplotlib` / `seaborn`

> Para mais detalhes sobre as dependências, confira `requirements.txt`.

## Observações

- Os dados brutos estão em `data/raw/`.
- Os dados processados ficam em `data/processed/`.
- As visualizações exportadas estão em `exports/figures/`.

