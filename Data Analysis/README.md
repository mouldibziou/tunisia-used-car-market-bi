# Data Analysis — The Tunisian Used Car Market

> **Notebook:** `analysisV2.ipynb`  
> **Author:** Mohamed Mouldi Bziou · October 2025  
> **Dataset:** ~4,900 records from tayara.tn + automobile.tn (July 2025 snapshot)  
> **Theme:** *"The Used Car Market in Tunisia: A Data-Driven Look Into Consumer Behavior and Economic Signals"*  
> **Companion outputs:** Power BI report (dynamic slicers, DAX measures) · [Plotly Dash web app](../Dashboard/) (deployed on Render)

---

## TL;DR — Key Findings at a Glance

| Signal | Value |
|--------|-------|
| **Market Leader** | Volkswagen — 13% share, avg 60K TND |
| **Median Price** | 38K TND (~24 months of average salary) |
| **Price-to-Income Ratio** | 2.65 years (51% above emerging-market average) |
| **Regional Concentration** | Greater Tunis = ~62% of all transactions |
| **Luxury Concentration** | Grand Tunis = 777 luxury cars; coastal = 2× luxury density |
| **EV/Hybrid Adoption** | 3.8% of market — newest avg year (2021), growing |
| **Consumer Preference** | 70% petrol · 1.2–1.6L engine · manual transmission · city cars |
| **Fiscal Power Correlation** | r = 0.60 — strongest individual price driver |
| **Price Ceiling** | 75% of transactions under 79K TND |
| **Accessible Tier Disappearing** | <5% of listings priced 10–20K TND |

---

## Visualization Strategy — Three Complementary Formats

The findings from this analysis are deliberately published in three formats to serve different audiences:

| Format | Tool | Purpose |
|--------|------|---------|
| **This notebook** (`analysisV2.ipynb`) | `matplotlib`, `seaborn`, `plotly` | Full reproducibility — code, narrative, and charts in one document; targets technical reviewers and data scientists |
| **Power BI report** | Power BI Desktop, DAX | Business-facing executive dashboard with dynamic slicers (brand, region, fuel, year range) — no code required to explore |
| **Plotly Dash web app** | Plotly Dash, gunicorn, Render | Deployed public web application for buyers and sellers to interactively track brand/model price trends over time |

All three consume the same underlying `2025_data.csv` dataset, ensuring consistency across outputs.

---

## Libraries & Tools

| Library | Version Used | Purpose |
|---------|-------------|---------|
| `pandas` | — | Aggregations, filtering, groupby |
| `numpy` | — | Percentiles, polynomial trend fitting |
| `matplotlib` | — | Multi-subplot figure compositions |
| `seaborn` | whitegrid theme | Statistical charts, heatmaps, regplots |
| `geopandas` | — | Choropleth maps of Tunisia ADM1 regions |
| `rapidfuzz` | — | Fuzzy location string matching |
| `plotly.express` | — | Interactive 3D scatter plots |
| `scipy.stats` | — | Correlation coefficient calculations |

---

## Notebook Structure — 7 Analysis Sections

### Section 1 · Market Structure Analysis

**Technique:** 3×2 subplot grid using `sns.set_theme('whitegrid')` with `sns.barplot`, `sns.countplot`, and custom pie charts.

**Charts produced:**
- Top 10 brands by listing count
- Top 10 models by listing count
- Body type distribution
- Fuel type distribution
- Brand origin distribution
- Engine-size distribution (bimodal)

**Key findings:**
- Volkswagen leads with ~13% market share (avg 60K TND)
- German brands collectively represent ~32% of market
- French brands: ~21%
- Bimodal engine-size distribution peaks at **1.2L and 1.6L**
- Citadines (city cars) are the dominant body type

---

### Section 2 · Vehicle Lifecycle Patterns

**Technique:** 1×3 subplot — registration year histogram with `axvline` annotations, car-age histogram with IQR shading, average price per registration year line chart.

**Charts produced:**
- Registration year histogram (vertical lines at 2011 and 2020)
- Car-age histogram with IQR annotations
- Average price per year (highlighting COVID-19 price surge)

**Key metrics:**
- 50% of listed cars are under **7.2 years** old
- 38% of cars are sold at **2.7–6 years** age — peak resale window
- Post-2020 exponential price surge attributed to COVID-19 supply disruption and currency depreciation

---

### Section 3 · Commercial vs. Consumer Segments

**Technique:** 2×3 subplots — pie chart for segment split, boxplots, bar charts, scatter plots coloured by year.

**Charts produced:**
- Commercial vs. consumer split (pie chart)
- Price boxplot by segment
- Top regions for commercial vehicles
- Price vs. mileage scatter coloured by registration year
- Brand frequency + price combo chart
- Mileage histogram

**Key metrics:**
| Metric | Commercial | Consumer |
|--------|-----------|----------|
| Market share | 5.7% | 94.3% |
| Avg price | 40,270 TND | — |
| Typical mileage | 170,000–200,000 km | < 120,000 km |
| Top brands | Peugeot, Citroën | VW, Renault, Kia |

---

### Section 4 · Geographic Market Segmentation

**Techniques:**
- **`geopandas` choropleth mapping** using `geo_merged.plot(column=..., cmap='Blues', legend=True)`
- **Fuzzy string matching** via `rapidfuzz.process.extractOne(name, map_names, scorer=fuzz.WRatio)` with threshold score ≥ 70 — falls back to manual correction dict for unmatched names
- GeoJSON source: `geoBoundaries-TUN-ADM1.geojson` (ADM1 governorate boundaries)

**Three choropleth maps produced:**
1. **Average price distribution** per governorate (Blues colormap)
2. **Luxury vehicle count** per governorate — luxury defined as set of 20 brands (Mercedes-Benz, BMW, Audi, Porsche, Land Rover, Jaguar, Volvo, etc.)
3. **Dominant body type** per governorate (mode per region)

**Key findings:**
- Grand Tunis: **777 luxury cars** — near-zero in interior regions
- National price range: **35K–80K TND** across governorates
- **19 of 24** governorates have city cars (citadines) as dominant body type
- Coastal cities show 2× the luxury concentration of inland regions

**Code pattern:**
```python
from rapidfuzz import process, fuzz

def best_match(name):
    match, score, _ = process.extractOne(name, map_names, scorer=fuzz.WRatio)
    return match if score >= 70 else None

df['map_region'] = df['location'].apply(best_match)
```

---

### Section 5 · Consumer Behavior & Brand Origin Analysis

**Technique:** 4-subplot figure — avg price by origin barplot, frequency by origin barplot, dominant body type per origin scatterplot, avg registration year by origin horizontal barplot.

**Price tier hierarchy by origin:**

| Price Tier | Origin | Avg Price |
|-----------|--------|----------|
| Ultra-Luxury | Swedish (Volvo) | 140K+ TND |
| Luxury | British (Land Rover, Jaguar) | 100–130K TND |
| Premium | German (VW, BMW, Mercedes, Audi) | ~85K TND |
| Mid-Range | Korean/Japanese | ~60K TND |
| Budget | French (Peugeot, Renault, Citroën) | ~40K TND |
| Entry-Level | Chinese (Chery, Geely, BYD) | ~60K TND* |

*Chinese avg elevated by newest vehicles in market (avg reg year 2021)*

**Market share by origin:**
- German: **32%** | French: **21%** | Asian: **23%** | Chinese: **4%** | Other: **20%**

**Market transition signal:** Chinese brands (avg year 2021) are the newest entrants; Japanese/German/French brands average reg year ~2015, reflecting historical dominance.

---

### Section 6 · Price Clustering & Affordability

**Technique:** 1×3 subplot — KDE histogram with `axvspan` shading, cumulative distribution function (CDF) with `np.sort` + `np.arange`, horizontal bar chart for affordability segments.

**Charts produced:**
1. Car price distribution (histogram + KDE, median/percentile annotated)
2. Cumulative distribution with 25th/50th/75th/90th percentile markers
3. Affordability segment bar chart (Accessible / Mid-range / Premium / Luxury)

**Key metrics:**

| Metric | Value |
|--------|-------|
| Peak concentration | 35–40K TND (11.2% of transactions) |
| 75th percentile | 79,500 TND |
| Median price | ~50K TND |
| Price-to-Income Ratio | **2.65 years** (32 months of full salary) |
| Monthly avg income | 1,570 TND |
| Accessible tier (<20K TND) | ~5% — **disappearing** |
| Mid-range (20–50K TND) | ~48% — stable |
| Premium (50–95K TND) | ~32% — growing |
| Luxury (>95K TND) | ~15% — growing |

**Comparative context:** Developed markets typically show a price-to-income ratio of 0.5–0.8 years. Tunisia at 2.65 years is **51% above the emerging market average of 1.2–1.5 years**, indicating severe market distortion from import taxes, currency depreciation, and dealer pricing.

---

### Section 7 · What the Market Loves (Pricing Drivers & Specs)

#### 7a · Correlation Heatmap

**Technique:** `df.corr(numeric_only=True)` → `sns.heatmap(annot=True, fmt='.2f', cmap='Blues')`

**Correlation with price:**

| Feature | r-value | Interpretation |
|---------|---------|---------------|
| Fiscal power | **+0.60** | Strongest driver — tax burden separates luxury from economy |
| Mileage | **−0.38** | Depreciation signal |
| Registration year | **+0.36** | Newer = premium |
| Engine size | **+0.31** | Weakest — tax matters more than displacement |

> Practical insight: A car at 7HP fiscal power costs ~300 TND/year in vignette; at 12HP it costs ~900 TND/year — perpetual cost burden drives market segmentation.

#### 7b · Market Leaders & Specs

**Technique:** Dual-axis bar+line chart (`twinx()`), scatter with `np.polyfit` quadratic trend, grouped bar chart for transmission types.

**Top 5 brand rankings:**

| Rank | Brand | Top Model | Avg Model Price |
|------|-------|-----------|----------------|
| 1 | Volkswagen | Golf | 66K TND |
| 2 | Renault | Clio | 37K TND |
| 3 | Kia | Rio | 51K TND |
| 4 | BMW | 3 Series | 80K TND |
| 5 | Kia | Sportage (top SUV) | 90K TND |

**Transmission analysis:**

| Type | Market Share | Avg Price | Avg Year |
|------|-------------|----------|---------|
| Manual | ~60% | 43,500 TND | 2015 |
| Automatic | ~40% | 104,000 TND | 2018 |

> Automatic premium of +139% (60,500 TND) is driven by luxury-segment positioning, not purely production cost.

#### 7c · Fuel Type Economics

**Technique:** 2×3 subplot — pie chart with `wedge.theta` custom label placement, boxplot, barplots (engine size, fiscal power per fuel type), bubble scatter (avg year vs fuel, bubble size = avg price), most-common-model barplot using `idxmax()` trick.

**Fuel market composition:**

| Fuel | Share | Avg Price | Avg Reg Year |
|------|-------|----------|-------------|
| Petrol (essence) | **70.3%** | ~59,400 TND | 2016 |
| Diesel | 26% | ~68,000 TND | 2014 |
| Hybrid | 2.8% | ~174,000 TND | 2021 |
| Electric | 1% | ~157,000 TND | 2021 |

**Policy insight:** Diesel pays 3× the annual vignette tax vs. petrol, making it financially impractical except for high-mileage drivers. Electric vehicles pay an 8HP tax despite zero emissions — a policy misalignment that retards EV adoption.

#### 7d · Transaction Density (Geographic)

**Technique:** `geopandas` choropleth (single map), frequency aggregation via `groupby('map_region')['price'].count()`.

| Region | Transaction Share |
|--------|-----------------|
| Greater Tunis (Tunis, Ariana, Ben Arous, Manouba combined) | **~62%** |
| Tunis alone | ~32% |
| Sousse | 365 listings |
| Sfax | ~300 listings |
| Nabeul | 274 listings |
| Mahdia (lowest density) | 67 listings |

**Structural finding:** Market liquidity directly mirrors urbanization and employment density — coastal corridor (Tunis–Sousse–Sfax–Nabeul) drives ~80% of market activity.

---

## Data Pipeline

```
final_data/2025_data.csv (~4,900 rows)
         │
         ▼
  analysisV2.ipynb
  ├── Market Structure Analysis
  ├── Vehicle Lifecycle Patterns
  ├── Commercial vs Consumer Segments
  ├── Geographic Segmentation (geopandas + rapidfuzz)
  ├── Brand Origin Analysis
  ├── Price Clustering & Affordability
  └── Pricing Drivers & Consumer Preferences
         │
         ▼
  Visualizations saved to figures/
```

---

## Notable Techniques

| Technique | Implementation | Purpose |
|-----------|---------------|---------|
| Fuzzy geo-matching | `rapidfuzz.process.extractOne` with WRatio scorer, threshold 70 | Map raw location strings → ADM1 shapefile names |
| Dual-axis charts | `ax.twinx()` | Overlay count bars with avg-price line |
| Polynomial trend | `np.polyfit(x, y, 2)` + `np.poly1d` | Engine-size vs. price quadratic trend line |
| Cumulative distribution | `np.sort` + `np.arange / len * 100` | Affordability access visualization |
| Geopandas choropleth | `GeoDataFrame.plot(column=..., cmap='Blues', legend=True)` | Regional price/luxury/body-type maps |
| Pie wedge labelling | `wedge.theta2 + wedge.theta1 / 2` angle calculation | Custom label placement outside pie segments |
| Segment counting | `df[(df['price'] >= lower) & (df['price'] < upper)]` | Four-tier affordability breakdown |

---

## Economic Context

The analysis situates price data within Tunisia's macro-economic reality:

- **Average monthly salary:** 1,570 TND (2025 estimate)
- **Annual income:** ~18,840 TND
- **Median car price / annual income:** 2.65× — classified as *severely unaffordable* by global standards
- **Inelastic demand driver:** Lack of reliable public transport infrastructure forces car ownership even at unaffordable price points, preventing market self-correction
- **COVID-19 impact:** Exponential price surge post-2021 tied to global supply chain disruption + TND currency depreciation

---

## Figures Directory

All charts are saved to `figures/` (see [figures/README.md](figures/README.md)).
