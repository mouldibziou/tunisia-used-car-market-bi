# Data Wrangling

This folder contains all notebooks responsible for cleaning, transforming, and integrating the raw scraped data. Each notebook corresponds to one data source, and a final merging notebook produces the unified datasets used in all downstream analysis.

---

## Pipeline Overview

```
automobile.tn raw CSV  ──▶  automobile_tn_wrangling.ipynb  ──▶  automobiletn_set.csv
tayara.tn raw CSV      ──▶  tayara_tn_wrangling.ipynb      ──▶  tayara_tn_standardized.csv
wayback raw CSV        ──▶  tunisie_annonce_wrangling.ipynb ──▶  tunisie_annonce_standardized.csv
                                        │
                              data_merging.ipynb
                                        │
               ┌────────────────────────┴────────────────────────┐
               ▼                                                 ▼
       2025_data.csv                                   historical_data.csv
    (tayara + automobile)                         (tunisie-annonce archive)
```

---

## `automobile_tn_wrangling.ipynb`

**Input:** `data_collection/automobile.tn/cleaned_automobile_tn.csv`  
**Output:** `csv/automobiletn_set.csv`

### Steps & Techniques

| Step | Technique |
|---|---|
| Column pruning | Dropped `interior` and `link` (non-informative) |
| Numeric extraction | `re.search(r'(\d+\.?\d*)')` strips units like "km", "TND", "CV" and casts to `int` |
| Date parsing | Regex distinguishes `DD.MM.YYYY` (publish dates) vs `MM.YYYY` (circulation dates) — two separate `datetime.strptime` formats |
| Case normalisation | All string columns lowercased via `str.map(lambda x: x.lower())` |
| Mean date imputation | `publish-date` NaNs filled with the column mean |
| Car-age feature engineering | `car-age` in months computed as `(avg_publish_date - circulation_date).days / 30.42` — a continuous numeric feature for regression models |
| Grouped median imputation | `engine-size` NaNs filled using `groupby(['brand','model','fuel','gear']).transform('median')` — leverages group context |
| **ML imputation — Location** | `DecisionTreeClassifier` trained on known `location` rows using `price`, `brand`, `model`, `body-type` (one-hot encoded); predictions fill missing locations |
| **ML imputation — Engine size** | `RandomForestRegressor` (200 estimators, `max_depth=10`) trained on known engine-sizes; categorical features one-hot encoded; `X.reindex` aligns feature space between train and predict sets |
| Electrical vehicles | `engine-size` set to `0` for `fuel == 'electrique'` before RF pass |
| Grouped median for dates | `groupby('model').transform(lambda x: x.fillna(x.median()))` fills remaining missing circulation dates |
| Engine rounding | Rounded to nearest 100cc for standardisation |
| Outlier removal | Two specific outlier rows with non-logical mileage values dropped by index |

---

## `tayara_tn_wrangling.ipynb`

**Input:** `data_collection/tayara.tn/tayara_tn.csv`  
**Output:** `csv/tayara_tn_standardized.csv`

### Steps & Techniques

| Step | Technique |
|---|---|
| Rental ad removal | Regex mask: drops rows where title or description contains `location`, `كرا`, or `louer` |
| Numeric cleaning | Same `re.sub(r'[^0-9.]', '', ...)` approach for mileage, engine-size, and fiscal-power |
| Relative date parsing | Publish dates were stored as relative strings (e.g., "3 months ago", "a day ago"); a custom function back-calculates absolute dates from a fixed collection date of **July 10, 2025** |
| Price normalisation | Prices below 500 treated as thousands (e.g., 47 → 47,000 TND); repeated-digit prices (111, 222…) mapped to 0 then to `NaN` |
| Mileage normalisation | Values under 400 multiplied by 1,000 (same unit inconsistency); values > 500,000 or < 5,000 dropped |
| Engine-size unit conversion | Values in litres (e.g., 1.6) multiplied by 1,000 → cc |
| Circulation date validation | Regex `\d{4}` ensures year-only format; dates outside 1978–2024 dropped |
| Random date suffix injection | Since only year was available, a random `MM-DD` is generated per row to create a full `datetime` object for car-age calculation |
| Car-age computation | `(publish_date - circulation_date)` in months |
| High fiscal-power cap | Values ≥ 35 CV treated as invalid and set to `NaN` |

---

## `tunisie_annonce_wrangling.ipynb`

**Input:** `data_collection/wayback/wayback_data.csv`  
**Output:** `csv/tunisie_annonce_standardized.csv`

This notebook handles the most complex wrangling task: the historical dataset extracted from archived HTML had minimal structured fields, so several features were **reverse-engineered from free-text descriptions**.

### Steps & Techniques

| Step | Technique |
|---|---|
| Brand/model filtering | 200+ irrelevant brands (motorcycles, boats, accessories) removed via regex pattern matching; valid car models whitelist (~150 entries) used to filter rows |
| **NLP — Fuel extraction** | `re.search` on lowercased description for keywords: `essence`, `diesel`, `mazout`, `gasoil` |
| **NLP — Fiscal power extraction** | `re.search(r'\b(\d+)\s*cv\b')` extracts horsepower directly from ad text |
| **NLP — Mileage extraction** | `re.search(r'(\d[\d\s]*)\s*kms?\b')` extracts mileage figures from descriptions |
| Model typo correction | Manual mapping dict applied via `str.replace` and direct `.loc` assignments (e.g., "Golf 1 & 2" → removed, "Série.3" → "Série 3") |
| AI-assisted data generation | 10 synthetic Mercedes GL-class rows generated with realistic attributes (AI-assisted) to fill a gap where all GL entries had been dropped due to model disambiguation — noted in code comments |
| Location standardisation | 200+ sub-district location names mapped to 24 standard Tunisian governorate names to match the taxonomy used in the 2025 datasets |
| **IQR outlier filtering** | `groupby(['brand','year']).apply(iqr_filter)` — per brand-year group, prices outside `[Q1 − 1.5×IQR, Q3 + 1.5×IQR]` are removed; prevents outlier prices in rare brand-year combinations from skewing the dataset |
| Price sanity filters | Drops: prices = 1, repeated-digit prices, < 2,000 TND, relatively new cars priced < 5,000 TND, cars > 9 years old priced > 150,000 TND |
| Deduplication on (date, price) | `drop_duplicates(subset=['circulation-date', 'price'])` removes cross-scrape duplicates |

---

## `data_merging.ipynb`

**Inputs:** all three standardised CSVs above  
**Outputs:** `final_data/2025_data.csv`, `final_data/historical_data.csv`

### Steps & Techniques

| Step | Technique |
|---|---|
| Luxury brand downsampling | `am_luxury.sample(frac=0.42, random_state=42)` — automobile.tn over-represented premium brands; 42% random sample retains variety while reducing bias |
| `pd.concat` merge | 2025 datasets (tayara + automobile.tn) concatenated into `df_2025`; historical dataset processed separately |
| Model typo normalisation | `model_map` dict (~50 entries) resolves variant names: `golf 4/5/6/7` → `golf`, `série 1/2/4` → `série 3`, `megane cc` → `megane`, etc. |
| **ML imputation — Fiscal power** | `RandomForestRegressor` trained on rows where fiscal-power is known; features = all columns except price, dates, and target; one-hot encoded and aligned via `X.align(..., join='left', fill_value=0)` |
| **ML imputation — Car age** | Same RF pattern for missing `car-age` values |
| **ML imputation — Price** | `RandomForestRegressor` with `LabelEncoder` on categoricals (not one-hot, to contain dimensionality); `X_complete.median()` used to fill any remaining feature NaNs before fitting; predicted prices rounded to nearest 1,000 TND |
| Fuel type mapping | Normalises hybrid variants: `hybride rechargeable essence` → `hybride essence`, `hybride léger diesel` → `hybride diesel`, etc. |
| Body type mapping | Merges fine-grained body types: `citadine` → `compacte`, `coupé` → `berline`, `autres` → `utilitaire` |
| Car origin feature | `origin` column mapped from brand name to country group (german, french, japanese, korean, chinese, etc.) using a 60-entry lookup dict |
| **Body type correction (2025 data)** | `correct_body_type(model)` function: a 100-entry model-name → body-type lookup table fixes systematic misclassification (e.g., city cars like Clio/Rio/Yaris were tagged `compacte` instead of `citadine`) |
| **Body type engineering (historical data)** | `add_body_type(df)` function: 250-entry `(brand, model)` tuple lookup dict assigns body types to the historical dataset which had none — partially AI-assisted |
| Date feature extraction | `publish-date` decomposed into `month` and `quarter` columns for time-series use |

---

## Output Files

| File | Rows | Description |
|---|---|---|
| `csv/automobiletn_set.csv` | ~2,000 | Cleaned automobile.tn listings |
| `csv/tayara_tn_standardized.csv` | ~3,000 | Cleaned tayara.tn listings |
| `csv/tunisie_annonce_standardized.csv` | ~4,500 | Cleaned historical listings |
| `final_data/2025_data.csv` | ~4,900 | Merged 2025 market dataset |
| `final_data/historical_data.csv` | ~4,500 | Historical dataset (2007–2024) |

---

## Libraries Used

| Library | Purpose |
|---|---|
| `pandas` | Core data manipulation |
| `numpy` | Numerical operations and NaN handling |
| `re` | Regex-based text extraction and cleaning |
| `datetime` | Date arithmetic and parsing |
| `sklearn.tree.DecisionTreeClassifier` | Location imputation |
| `sklearn.ensemble.RandomForestRegressor` | Engine-size, fiscal-power, car-age, and price imputation |
| `sklearn.preprocessing.LabelEncoder` | Categorical encoding for RF price model |
| `seaborn`, `matplotlib` | Outlier visualisation (boxplots) |
