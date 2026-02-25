# Exploratory Data Analysis (EDA)

This folder contains two EDA notebooks that provide a comprehensive statistical and visual exploration of both the **2025 snapshot** and the **2007–2024 historical** datasets. The goal is to understand data distributions, identify patterns, validate assumptions, and surface economic signals before deeper analysis.

---

## Notebooks

| Notebook | Dataset | Records |
|---|---|---|
| `2025_EDA.ipynb` | `final_data/2025_data.csv` | ~4,900 |
| `historical_data_EDA.ipynb` | `final_data/historical_data.csv` | ~4,500 |

---

## `2025_EDA.ipynb` — Current Market Snapshot

### Libraries
`pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy.stats`, `plotly.express`

---

### 1. Univariate Analysis

**Numerical variables:** price, mileage, car-age, fiscal-power, engine-size, year

| Plot | Finding |
|---|---|
| Boxplots (all numerical cols, 1×N grid) | Right-skewed distributions across most variables; consistent high-end outliers across all columns reflecting the nature of the used car market |
| Histograms (all numerical cols) | Price range **36,000–85,000 TND** covers the bulk of listings; fiscal-power bimodal at **4 CV** and **6 CV**; engine-size multimodal, reflecting common engine categories |

**Categorical variables:** fuel, body-type, gear, origin  
**Special cases:** brand (top 12), model (top 15), location (pie chart)

| Plot | Finding |
|---|---|
| Bar charts | Economic brands (Peugeot, Kia, Renault, VW) dominate; ~65% manual gearbox; berline and compacte are the most frequent body types |
| Pie chart — location | Greater Tunis (Tunis + Ariana + Ben Arous) accounts for **>50%** of all listings |
| Bar chart — models | Golf, Série 3, Clio, Rio dominate — mostly berlines and compacts |

Mode of each categorical column reported via `df[cols].mode()`.

---

### 2. Bivariate Analysis

**Correlation heatmap** (`df.corr(numeric_only=True)`, `seaborn.heatmap`, `coolwarm`):

| Pair | Correlation | Insight |
|---|---|---|
| price ↔ fiscal-power | High | Prices increase with tax horsepower |
| mileage ↔ car-age | Highest | Older cars accumulate more mileage |
| engine-size ↔ fiscal-power | Moderate positive | Larger engines have higher fiscal power |

**Scatter plots** (generated for pairs with r > 0.5):
- `sns.regplot` — price vs. fiscal-power (full view + IQR-clipped view)
- `sns.scatterplot` — price vs. mileage; mileage vs. car-age
- engine-size vs. fiscal-power with anomaly detection

**Anomaly removal:** rows where engine-size ≥ 3,000 cc with fiscal-power < 11 CV, or engine-size ≤ 2,000 cc with fiscal-power > 12 CV are flagged as inconsistent and dropped. Fiscal-power = 0 rows also removed.

**Average price by category:**
- By fuel type — `groupby('fuel')[['price']].mean().sort_values()`
- By location — top 5 highest average prices
- By gear type per brand — stacked bar chart

**Diverging bar chart — premium vs. budget brands:** most and least expensive brands plotted back-to-back on a shared axis using container height negation. Porsche and Land Rover as most expensive; Chinese and Indian brands as cheapest.

---

### 3. Multivariate Analysis

| Visualisation | Technique | Finding |
|---|---|---|
| Body type × location × avg price | `pivot_table` + `idxmax()` + merge | Each location's most common body type mapped to its average price |
| Engine-size × fiscal-power by fuel | `sns.scatterplot(hue='fuel')` | Diesel tends to larger engines and higher fiscal power; EVs cluster at zero fiscal power |
| Mileage × location × fuel | `sns.barplot(estimator='mean', errorbar=None)` | Diesel highest mileage across all top-5 cities; electric lowest |
| Price × location × fuel | Same structure | Hybrid-petrol most expensive; Tunis peaks at ~175,000 TND for hybrids |
| **Interactive 3D scatter** | `plotly.express.scatter_3d` — engine-size, fiscal-power, price coloured by price (viridis) | Positive relationship visible across all three axes |

---

### Key Metrics Surfaced

| Metric | Value |
|---|---|
| Price range (75th percentile) | < 79,000 TND |
| Most common fuel type | Petrol (70%) |
| Dominant gearbox | Manual (65%) |
| Top location | Tunis (33% of listings) |
| Peak registration year | 2021 |
| 2020 COVID-19 dip | Clear drop in registrations |

---

## `historical_data_EDA.ipynb` — 18-Year Market Overview (2007–2024)

### Libraries
`pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy.stats`, `calendar`

---

### 1. Univariate Analysis

**Numerical variables:** year, car-age, fiscal-power, price, quarter, month

| Plot | Finding |
|---|---|
| Boxplots + Histograms | Bimodal year distribution with peaks around 2009 and 2016; most cars under 10 years old at time of listing; price majority below **33,825 TND** |
| Missing values bar chart | Visualised with `isnull().sum()` + `seaborn.barplot`; ~80% of mileage values missing — noted as non-critical for this analysis |
| Yearly frequency line chart | Average **225 listings per year** across the 18-year window |

**Categorical variables:** brand, model, fuel, location, body-type

| Finding |
|---|
| German and French brands dominate historically |
| Golf, Clio, Polo are top models |
| Petrol ~65% / Diesel ~35% split consistent across time |
| Citadine body type historically dominant (vs. berline in 2025) |
| Greater Tunis dominates geographic distribution |

---

### 2. Bivariate Analysis

**Correlation heatmap:** price ↔ fiscal-power moderate; car-age ↔ mileage stronger.

**Periodic trend analysis** (three separate line charts):
- Monthly average price — spikes in **June** and **December**
- Quarterly average price — **Q3** (summer/September) peaks
- Yearly average price — consistent upward trend, sharply steepening post-COVID

**Diverging bar chart — premium vs. budget brands:** Porsche and Land Rover highest; Chery's recent market entry inflates its ranking.

**Average mileage and price by fuel type:**
- Diesel higher mileage than petrol (expected)
- Near-identical average prices between petrol and diesel historically

**Monthly price distribution (12 boxplots, 2×6 grid):** May and October show higher price variability and more outliers.

---

### 3. Multivariate Analysis

**Mileage vs. Price coloured by year** (two scatter views — full and clipped):
- 2008/2011 data more spread-out → stronger market, weak mileage-price effect
- Recent years show strong negative mileage-price correlation
- High-mileage 2020 cars cluster with low-mileage 2011 cars → **inflation effect quantified visually**

**Yearly price evolution by fuel type** (`groupby(['year','fuel'])['price'].mean()`):
- Diesel prices consistently higher than petrol
- Noticeable post-2021 spike confirmed by external economic reports

**Brand × fuel average price** (top 7 brands):
- BMW shows largest petrol–diesel gap (petrol much higher)
- Renault and VW show balanced petrol/diesel pricing

**Top 3 models per brand** (2×4 subplot grid, bar labels with count):
- BMW Series 3 and Peugeot 206 lead their respective brands historically

---

### Conclusion Highlights from the Notebook

> "Nominal prices have generally risen over time, with a notable 50% increase in petrol car prices in 2021 compared to diesel."

> "A slight price increase after the 2011 Tunisian Revolution suggests the decrease of the local currency against the dollar, tied to an increase in demand."

> "The absence of ~80% of mileage values does not affect the analysis, as mileage was not used for predictive modeling."

---

## Shared Plot Patterns

Both notebooks follow the same structural approach:

1. `df.describe()` and `df.info()` baseline
2. Univariate → Bivariate → Multivariate progression
3. `plt.subplots` with `tight_layout()` for multi-panel figures
4. `sns.set_theme(style='whitegrid')` for consistent visual identity
5. Inline Markdown commentary after each visualisation to document findings
