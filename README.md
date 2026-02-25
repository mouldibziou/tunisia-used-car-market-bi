# Tunisia Used Car Market — End-to-End Data Science Project

**Author:** Mohamed Mouldi Bziou  
**Timeline:** 2025 – 2026  
**Status:** Active — forecasting module planned (see [Future Releases](#future-releases))

---

## Problem Statement

Tunisia's used car market is large, fragmented, and poorly documented. Listings are spread across multiple platforms with inconsistent formats, no standardised pricing, and no public data aggregation. The goal of this project is to:

1. **Collect** raw listings data from three distinct online sources
2. **Standardise and clean** heterogeneous, noisy data without discarding it through ML-based imputation
3. **Analyse** pricing dynamics, consumer behaviour, and economic signals embedded in the market
4. **Visualise** findings across three complementary formats — a self-contained Jupyter notebook analysis, an interactive Power BI report, and a deployed Plotly Dash web application — so that buyers, sellers, and analysts can explore the data themselves at different levels of depth

The result is a pipeline that turns unstructured web listings into a structured, analysis-ready dataset surfaced through three distinct visualization layers.

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1 · DATA COLLECTION                                      │
│                                                                 │
│  tayara.tn ──────────────────┐                                  │
│  automobile.tn ──────────────┼──► ~9,400 raw listings           │
│  tunisie-annonce.com         │    (via Wayback Machine CDX API) │
│  (2007–2024 archive) ────────┘                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│  STAGE 2 · DATA WRANGLING                                       │
│                                                                 │
│  Per-source cleaning ──► Feature engineering ──► ML imputation  │
│  Merge + dedup ──────────────────────────────► Final datasets   │
│                                                                 │
│  Output: 2025_data.csv (~4,900 rows)                            │
│          historical_data.csv (~4,500 rows)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│  STAGE 3 · EXPLORATORY DATA ANALYSIS                            │
│                                                                 │
│  Univariate → Bivariate → Multivariate                          │
│  Historical trend analysis · Seasonal patterns                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│  STAGE 4 · IN-DEPTH ANALYSIS                                    │
│                                                                 │
│  Market structure · Geographic segmentation · Affordability     │
│  Brand origin dynamics · Fuel economics · Economic signals      │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│  STAGE 5 · VISUALIZATION & REPORTING (3 formats)                │
│                                                                 │
│  📓 Jupyter Notebook  — inline charts, narrative, full code     │
│  📊 Power BI Report   — executive dashboard, dynamic slicers    │
│  🌐 Plotly Dash App   — deployed web app, brand/model explorer  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
Projects/
│
├── data_collection/          # Stage 1 — Web scraping notebooks
│   ├── automobile.tn/        #   Large link scraper + ad detail scraper
│   ├── tayara.tn/            #   Link harvester + full ad scraper
│   └── wayback/              #   Wayback Machine CDX API scraper
│
├── data_wrangling/           # Stage 2 — Cleaning, imputation, merging
│   ├── automobile_tn_wrangling.ipynb
│   ├── tayara_tn_wrangling.ipynb
│   ├── tunisie_annonce_wrangling.ipynb
│   ├── data_merging.ipynb
│   ├── csv/                  #   Intermediate per-source outputs
│   └── final_data/           #   2025_data.csv · historical_data.csv
│
├── EDA/                      # Stage 3 — Exploratory analysis
│   ├── 2025_EDA.ipynb
│   └── historical_data_EDA.ipynb
│
├── Data Analysis/            # Stage 4 — Deep-dive analysis & insights
│   └── analysisV2.ipynb
│
└── Dashboard/                # Stage 5 — Interactive Dash web app
    ├── run.py
    ├── app/
    │   ├── dashboard.py
    │   └── data_processor.py
    └── data/merged_data.csv
```

---

## Key Findings

| Signal | Value |
|--------|-------|
| Market leader | Volkswagen — 13% share, avg 60K TND |
| Median listing price | ~50K TND (~32 months of average salary) |
| Price-to-income ratio | **2.65×** annual income — 51% above emerging-market average |
| Regional concentration | Greater Tunis drives ~62% of all transactions |
| Luxury vehicle clustering | 777 luxury cars in Grand Tunis; near-zero in interior |
| EV/Hybrid adoption | 3.8% of market, avg registration year 2021 — fastest-growing segment |
| Primary consumer preference | Petrol (70%) · 1.2–1.6L engine · manual transmission · city car |
| Strongest price driver | Fiscal power (r = 0.60) — Tunisia's HP-based annual tax system |
| Post-COVID price surge | Exponential price increase post-2021 tied to supply chain disruption + TND depreciation |
| Chinese brand entry | 4% market share, avg year 2021 — fastest-expanding origin segment |

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| **Scraping** | `requests`, `BeautifulSoup` (lxml parser), `hashlib` (MD5 dedup) |
| **Archive access** | Wayback Machine CDX API (`web.archive.org/cdx/search/cdx`) |
| **Data manipulation** | `pandas`, `numpy`, `re` |
| **ML imputation** | `scikit-learn` — `RandomForestRegressor`, `DecisionTreeClassifier`, `LabelEncoder` |
| **Statistical analysis** | `scipy.stats` |
| **Visualisation (notebook)** | `matplotlib`, `seaborn`, `plotly`, `plotly.express` |
| **Geospatial analysis** | `geopandas` (ADM1 choropleth maps) |
| **Fuzzy string matching** | `rapidfuzz` (WRatio scorer, threshold 70) |
| **BI dashboard** | Power BI Desktop — dynamic slicers, DAX measures, executive report |
| **Web dashboard** | `Plotly Dash`, `dash.dcc`, `dash.html` |
| **Deployment** | `gunicorn`, Render (`render.yaml`), Heroku-style `Procfile` |
| **Environment** | Python 3.11, Anaconda |

---

## Visualization Outputs — Three Formats, One Dataset

The same cleaned dataset (`2025_data.csv` + `historical_data.csv`) is surfaced through three distinct visualization layers, each targeting a different audience and depth of interaction:

| Format | Tool | Audience | Location |
|--------|------|----------|----------|
| **Jupyter Notebook** | `matplotlib` · `seaborn` · `plotly` | Data scientists, technical reviewers | `Data Analysis/analysisV2.ipynb` |
| **Power BI Report** | Power BI Desktop (DAX, dynamic slicers) | Business analysts, non-technical stakeholders | `Data Analysis/` |
| **Plotly Dash Web App** | Plotly Dash · gunicorn · Render | General public, buyers, sellers | `Dashboard/` — deployed on Render |

This multi-format approach was deliberate: the notebook provides full reproducibility and narrative context, Power BI enables fast executive-level exploration without running code, and the Dash app makes the data publicly accessible through a browser.

---

## Notable Techniques

### ML-Based Imputation Instead of Row Dropping

Standard approaches drop rows with missing values. This project uses trained ML models to impute missing fields, preserving the full dataset:

| Missing Field | Method | Detail |
|--------------|--------|--------|
| `location` | `DecisionTreeClassifier` | Trained on brand, model, price, year |
| `engine-size` | `RandomForestRegressor` (200 estimators, max_depth=10) | Trained on fiscal power, fuel, brand |
| `fiscal-power` | `RandomForestRegressor` | Trained on engine size, brand, year |
| `car-age` | `RandomForestRegressor` | Trained on year, mileage, model |
| `price` (historical) | `RandomForestRegressor` | Used only for gap-filling in merge step |

This approach retains rows that would otherwise be lost, improving dataset completeness without introducing naive mean/median bias.

### Duplicate Detection Across Scraping Sessions

Web scrapers use MD5 hashing to avoid re-processing ads seen in previous sessions:

```python
import hashlib

ad_id = hashlib.md5(f"{title}-{price}-{location}".encode()).hexdigest()
if ad_id not in seen_ads:
    seen_ads.add(ad_id)
    # process ad
```

Hash sets are persisted to disk (`seen_ads.txt`) between runs, enabling incremental collection without full re-crawls.

### Fuzzy Location Matching for Geospatial Joins

Raw scraped location strings are unstructured free text. `rapidfuzz` maps them to official governorate names for choropleth mapping:

```python
from rapidfuzz import process, fuzz

def best_match(name):
    match, score, _ = process.extractOne(name, shapefile_names, scorer=fuzz.WRatio)
    return match if score >= 70 else None   # falls back to manual correction dict
```

### Adaptive CSS Selector Fallback (Scraping)

The automobile.tn detail scraper tries multiple CSS selectors in order, gracefully handling page structure variations without crashing:

```python
for selector in selector_candidates:
    result = soup.select_one(selector)
    if result:
        break
```

### Sparse Data Detection in Dashboard Charts

Price trend charts detect years with fewer than 5 data points and render them as **red diamond markers** rather than connecting them with a spline — preventing misleading trend lines from thin data:

```python
sparse_years = df[df['count'] < 5]['year'].tolist()
# Rendered as red diamonds; dense years rendered as solid blue spline
```

### Luxury Brand Downsampling

The 2025 dataset overrepresents luxury listings relative to market reality. A 42% random sample (`random_state=42`) is taken of luxury rows during the merge step to preserve realistic distribution without eliminating the segment.

---

## Data Sources

| Source | Period | Method | Records |
|--------|--------|--------|---------|
| [automobile.tn](https://www.automobile.tn) | 2025 | Paginated link crawl + detail scraper | ~3,000 |
| [tayara.tn](https://www.tayara.tn) | 2025 | Link harvester + detail scraper | ~1,900 |
| [tunisie-annonce.com](https://www.tunisie-annonce.com) | 2007–2024 | Wayback Machine CDX API | ~4,500 |

---

## Subfolder READMEs

Each stage has a dedicated README with full technical documentation:

- [data_collection/README.md](data_collection/README.md) — Scraper architecture, deduplication, Wayback API
- [data_wrangling/README.md](data_wrangling/README.md) — Cleaning logic, ML imputation, merge strategy
- [EDA/README.md](EDA/README.md) — Chart inventory, statistical findings, seasonal patterns
- [Data Analysis/README.md](Data%20Analysis/README.md) — 7 analysis sections, geospatial maps, economic signals
- [Dashboard/README.md](Dashboard/README.md) — Dash architecture, callbacks, deployment

---

## Running the Project

### Dashboard (quickest start)

```bash
cd Dashboard
pip install -r requirements.txt
python run.py
# Open http://127.0.0.1:8050
```

### Re-running the full pipeline

Execute notebooks in order:

```
data_collection/   →   data_wrangling/   →   EDA/   →   Data Analysis/   →   Dashboard/
```

> Note: Scraping notebooks require active internet access and will take several hours to collect fresh data. Processed CSVs in `data_wrangling/final_data/` can be used directly to skip to EDA.

---

## Future Releases

### Time Series Forecasting Module

The `historical_data.csv` dataset spans **2007–2024** (~4,500 records), providing 17 years of used car pricing data. The next major release will add a dedicated time series analysis and forecasting stage:

**Planned analyses:**
- **Price trend decomposition** — separating trend, seasonality, and residual components using `statsmodels` STL decomposition
- **Seasonal pattern quantification** — confirming and modelling the June/December price spikes and Q3 peak already observed in EDA
- **Brand-level forecasting** — per-brand price forecasts using ARIMA/SARIMA, allowing buyers to time purchases
- **Volatility modelling** — GARCH models on price series to measure market uncertainty across segments
- **Regime change detection** — identifying structural breaks (e.g., the 2021 COVID supply shock) using Chow test or PELT (Pruned Exact Linear Time)

**Planned models:**

| Model | Use Case |
|-------|---------|
| SARIMA / SARIMAX | Univariate price forecasting with seasonality |
| Prophet (Meta) | Trend + holiday-aware forecasting with uncertainty intervals |
| LSTM (PyTorch/Keras) | Deep learning approach for non-linear price patterns |
| XGBoost (time features) | Gradient boosting with lag features and rolling statistics |

**Target output:** A forecasting notebook (`Data Analysis/forecasting.ipynb`) + a new dashboard tab showing 12-month price projections per brand/model with confidence intervals.

**Data requirement:** The existing `historical_data.csv` is sufficient as a base; augmentation with quarterly macroeconomic indicators (TND/EUR exchange rate, fuel price index, import volume) is planned to improve SARIMAX exogenous regressors.
