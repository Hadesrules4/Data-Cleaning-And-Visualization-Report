# Data Cleaning & Visualization Project

A beginner-friendly Python project that cleans a deliberately messy retail sales dataset, audits data quality, and generates visual reports.

## Features
- Detects and removes duplicate rows
- Handles missing values and invalid entries
- Flags outliers using the 1.5 × IQR rule
- Imputes numeric values with medians and categorical values with modes
- Recalculates sales from quantity × unit price
- Generates five charts and a data-quality report

## Run on Windows
```bat
py -m pip install -r requirements.txt
py main.py
```

Open `reports/data_quality_report.txt` and the charts under `reports/charts/`.

## Project structure
- `main.py` — cleaning, analysis, charting, and report generation
- `data/raw/retail_sales_raw.csv` — intentionally messy sample dataset
- `data/processed/retail_sales_cleaned.csv` — cleaned output
- `reports/data_quality_report.txt` — audit and findings
- `reports/charts/` — generated charts
- `DATA_DICTIONARY.md` — field definitions and cleaning rules

The included retail data is synthetic and intended for learning. Cleaning decisions should be adapted to the business context when working with real data.
