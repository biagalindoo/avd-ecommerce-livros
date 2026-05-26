# Projeto Final - Analise e Visualizacao de Dados

Projeto da disciplina **Analise e Visualizacao de Dados com Python**.

## Tema

Analise de catalogo de livros em um ambiente de e-commerce, usando dados extraidos por web scraping do site publico [Books to Scrape](https://books.toscrape.com/).

## Objetivo

Construir um fluxo completo de ciencia de dados:

1. extrair dados brutos da web;
2. tratar e normalizar os dados com Pandas;
3. calcular metricas e estatisticas exploratorias;
4. criar visualizacoes orientadas por principios de Gestalt;
5. entregar um dashboard interativo em Streamlit.

## Estrutura

```text
.
|-- app/
|   `-- streamlit_app.py
|-- data/
|   |-- raw/
|   `-- processed/
|-- notebooks/
|-- scripts/
|-- src/
|   `-- avd_project/
|-- tests/
|-- requirements.txt
`-- README.md
```

## Como rodar

Crie um ambiente virtual e instale as dependencias:

```bash
python -m venv .venv
pip install -r requirements.txt
pip install -e .
```

Execute a extracao dos dados:

```bash
python scripts/run_scraping.py
```

Execute o tratamento dos dados:

```bash
python scripts/run_etl.py
```

Execute a analise estatistica exploratoria:

```bash
python scripts/run_analysis.py
```

Gere as visualizacoes em HTML:

```bash
python scripts/run_visualizations.py
```

Abra o dashboard interativo:

```bash
streamlit run app/streamlit_app.py
```

## Bonus de inovacao

O projeto inclui uma aba **ML** no dashboard com segmentacao K-Means. O modelo agrupa livros por preco, nota, valor percebido e tamanho do titulo para apoiar decisoes de catalogo.

As etapas do projeto serao adicionadas em commits pequenos.
