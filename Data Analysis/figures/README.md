# Figures Directory

Place exported figure images here before compiling the LaTeX report.

Each image is referenced from `tunisia_car_market_report.tex` using
`\includegraphics{figures/<filename>}`. Export them from the notebook cells
as PNG files (Plotly: use `.write_image()` or the download button;
Matplotlib/Seaborn: use `plt.savefig()`).

## Required figures

| Filename | Notebook Section |
|---|---|
| `market_overview_grid.png` | Section 2 — Market Overview & Composition |
| `mileage_age_distribution.png` | Section 2 — Mileage & Vehicle Age |
| `lifecycle_patterns.png` | Section 3 — Vehicle Lifecycle Patterns |
| `commercial_segment_analysis.png` | Section 4 — Commercial Vehicles |
| `geographic_analysis.png` | Section 5 — Geographic Segmentation |
| `brand_origin_analysis.png` | Section 6 — Brand Origin |
| `price_affordability.png` | Section 7 — Affordability |
| `fuel_type_analysis.png` | Section 8 — Fuel Type Economics |
| `transaction_density_map.png` | Section 9 — Transaction Density |
| `correlation_heatmap.png` | Section 10 — Correlation Analysis |
| `market_leaders_pricing.png` | Section 10 — Market Leaders |

## Tips

- Recommended export size: **1400 × 700 px** (wide) or **900 × 900 px** (square)
- Use `dpi=150` for matplotlib figures to keep file sizes reasonable
- Plotly: `fig.write_image("figures/xxx.png", width=1400, height=700, scale=1.5)`
- If a figure is not yet ready, comment out its `\includegraphics` line in the .tex
  file — the document will still compile.
