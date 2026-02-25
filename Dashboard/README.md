# Dashboard  Interactive Used Car Market Explorer

> **Framework:** Plotly Dash (Python)
> **Entry Point:** `run.py`
> **App Class:** `TunisiaCarDashboard` in `app/dashboard.py`
> **Data Processor:** `CarDataProcessor` in `app/data_processor.py`
> **Deployment:** Render (`render.yaml`) or Heroku-style (`Procfile`) via `gunicorn`
> **Default Port:** 8050

---

## Overview

An interactive web dashboard for exploring Tunisia's used car market data. Users can drill into any brand -> model combination across a configurable year range and inspect pricing trends, market insights, and data quality flags  all generated dynamically from the underlying dataset.

---

## Architecture

```
run.py                      <- Entry point; data loading, validation, server export
app/
  __init__.py
  dashboard.py              <- TunisiaCarDashboard class (layout + callbacks)
  data_processor.py         <- CarDataProcessor class (load, clean, aggregate)
  utils.py                  <- Shared helpers
assets/
  style.css                 <- Custom dashboard styling
data/
  merged_data.csv           <- Combined 2025 + 2007-2024 dataset (~9,000+ rows)
```

---

## Data Pipeline

### `CarDataProcessor` (`data_processor.py`)

Handles loading and transformation of the two source datasets into a unified schema.

#### Loading

```python
processor = CarDataProcessor()
df_2025   = processor.load_2025_data()       # ~4,900 rows - tayara.tn + automobile.tn
df_hist   = processor.load_historical_data() # ~4,492 rows - tunisie-annonce.com (2007-2024)
```

Both datasets are standardised to a **common 12-column schema** with a `source` column distinguishing origin.

#### `clean_and_transform(df)`

| Step | Implementation | Detail |
|------|---------------|--------|
| Outlier removal | Drop top 1% of prices | Removes extreme luxury outliers |
| String normalisation | `.str.strip().str.title()` on brand/model | Ensures consistent capitalisation |
| Year filter | Keep `2000 <= year <= 2025` | Removes data errors |
| Price categorisation | `pd.cut` into 5 bins | Budget / Economy / Mid-range / Premium / Luxury |

#### `aggregate_for_analysis(df)`

Returns a yearly market trend (mean price per year) used for the global trend toggle.

---

### `run.py`  Entry Point & Validation

`run.py` performs pre-flight validation before handing data to the dashboard:

| Validation Step | Logic |
|----------------|-------|
| Column normalisation | Replace `-` with `_` in all column names |
| Car-age calculation | `car_age = current_year - year` (if column missing) |
| Drop critical NaN rows | Removes rows with null `brand`, `model`, `year`, or `price` |
| Year range filter | Keep `2000 <= year <= 2025` |
| Price sanity check | Keep `price > 0` |
| gunicorn export | `server = app.server` (Flask instance exposed for WSGI) |

**Environment variable:**
```bash
DASHBOARD_DATA_PATH=/path/to/custom/merged_data.csv
```
Defaults to `data/merged_data.csv` if not set.

---

## Dashboard Features  `TunisiaCarDashboard` (`dashboard.py`)

### Layout Components

Built with `dash.html` and `dash.dcc` components:

| Component | Type | Behaviour |
|-----------|------|-----------|
| Brand selector | `dcc.Dropdown` | Single-select; triggers model update callback |
| Model selector | `dcc.Dropdown` | Cascading  options depend on selected brand |
| Year range | `dcc.RangeSlider` | Min/max from dataset; filters both chart and insights |
| Market trend toggle | `dcc.Checklist` | Overlays overall yearly avg on brand/model chart |

### Callbacks  `_register_callbacks()`

#### Callback 1: Model Dropdown Update

```python
@app.callback(
    Output('model-dropdown', 'options'),
    Input('brand-dropdown', 'value')
)
```

Filters available models to those belonging to the selected brand, enabling **cascading dropdowns**.

#### Callback 2: Chart + Insights Update

```python
@app.callback(
    [Output('price-chart', 'figure'),
     Output('insights-panel', 'children')],
    [Input('brand-dropdown', 'value'),
     Input('model-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('trend-toggle', 'value')]
)
```

Triggers on any filter change and regenerates both the chart and the stats panel.

---

### Chart Rendering  `_aggregate_data()` + Sparse Data Detection

```python
def _aggregate_data(brand, model, year_range):
    # Groups by brand/model/year
    # Returns: mean price, median price, count, std price per year
```

**Sparse data detection:** Years with fewer than 5 data points are flagged and rendered differently:

| Data density | Visual style |
|-------------|-------------|
| >= 5 samples | Solid blue line with **spline smoothing** |
| < 5 samples | **Red diamond markers** (sparse warning) |

This prevents misleading trend lines from single-point years.

---

### Insights Panel  `_generate_insights()`

Automatically computed for every filter state:

| Metric | Calculation |
|--------|------------|
| **Price evolution %** | `(latest_price - earliest_price) / earliest_price * 100` |
| **Volatility** | `std / mean * 100` (coefficient of variation) |
| **Sparse year warnings** | List of years with < 5 samples flagged in the UI |
| **Price growth annotation** | Displayed directly on chart as text overlay |

---

## `_get_market_trend()`

When the market-trend toggle is enabled, this method computes the **overall yearly average price across all brands/models** and overlays it on the current chart as a reference line  allowing users to compare a specific model's trajectory against the broad market.

---

## Deployment

### Local Development

```bash
pip install -r requirements.txt
python run.py
# Dashboard available at http://127.0.0.1:8050
```

### Production  Render

Configured via `render.yaml`:

```yaml
services:
  - type: web
    startCommand: gunicorn run:server
```

### Production  Heroku-style

```
# Procfile
web: gunicorn run:server
```

### Runtime

```
# runtime.txt
python-3.11.x
```

---

## Requirements

Key dependencies from `requirements.txt`:

| Package | Role |
|---------|------|
| `dash` | Core web framework + components |
| `plotly` | Chart rendering (line charts, markers) |
| `pandas` | Data aggregation and filtering |
| `numpy` | Statistical calculations |
| `gunicorn` | Production WSGI server |

---

## Dataset

| Dataset | Rows | Source |
|---------|------|--------|
| 2025 snapshot | ~4,900 | tayara.tn + automobile.tn |
| Historical (2007-2024) | ~4,492 | tunisie-annonce.com via Wayback Machine |
| **Combined** | **~9,400** | `data/merged_data.csv` |

The combined dataset spans **18 years** of Tunisian used car listings, enabling longitudinal price trend analysis across all brands and models.

---

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Sparse data (< 5 samples) rendered as red markers | Prevents spline smoothing from connecting unreliable single-year data points |
| `std/mean * 100` volatility metric | Normalised (CoV) allows fair comparison across price ranges |
| Cascading dropdowns | Prevents invalid brand/model combinations from being selected |
| gunicorn `server` export | Standard Dash production deployment pattern via `app.server` |
| `DASHBOARD_DATA_PATH` env var | Enables flexible deployment without hardcoded paths |

---

## Public Repo Checklist

Before pushing publicly, verify:

- No personal data is included in any committed CSV/HTML/debug artifacts.
- No API tokens, passwords, or private keys are present in code or notebooks.
- Large raw intermediate files are excluded if not needed for reproducibility.
- `.env` files are not committed.
- Paths in processing code are relative to the project layout for portability.
