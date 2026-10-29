"""Data Cleaning & Visualization project. Run with: python main.py"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parent
RAW_FILE = ROOT / "data" / "raw" / "retail_sales_raw.csv"
CLEAN_FILE = ROOT / "data" / "processed" / "retail_sales_cleaned.csv"
REPORT_DIR = ROOT / "reports"
CHART_DIR = REPORT_DIR / "charts"
REPORT_FILE = REPORT_DIR / "data_quality_report.txt"
sns.set_theme(style="whitegrid")


def load_data(path):
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path)


def clean_data(df):
    data = df.copy()
    original_rows = len(data)
    missing_before = int(data.isna().sum().sum())
    for col in ["product", "region", "sales_channel"]:
        data[col] = data[col].astype("string").str.strip().replace("", pd.NA)
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    for col in ["quantity", "unit_price", "customer_rating", "sales"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    duplicate_count = int(data.duplicated().sum())
    data = data.drop_duplicates().copy()
    data.loc[data["quantity"] <= 0, "quantity"] = pd.NA
    data.loc[data["unit_price"] <= 0, "unit_price"] = pd.NA
    data.loc[~data["customer_rating"].between(1, 5), "customer_rating"] = pd.NA
    outlier_counts = {}
    for col in ["quantity", "unit_price", "customer_rating"]:
        valid = data[col].dropna()
        if valid.empty:
            outlier_counts[col] = 0
            continue
        q1, q3 = valid.quantile([0.25, 0.75])
        iqr = q3 - q1
        mask = (data[col] < q1 - 1.5 * iqr) | (data[col] > q3 + 1.5 * iqr)
        outlier_counts[col] = int(mask.sum())
        data.loc[mask, col] = pd.NA
    for col in ["product", "region", "sales_channel"]:
        mode = data[col].mode(dropna=True)
        data[col] = data[col].fillna(mode.iloc[0] if not mode.empty else "Unknown")
    for col in ["quantity", "unit_price", "customer_rating"]:
        median = data[col].median()
        data[col] = data[col].fillna(median if pd.notna(median) else 0)
    before_dates = len(data)
    data = data.dropna(subset=["order_date"]).copy()
    invalid_dates = before_dates - len(data)
    data["quantity"] = data["quantity"].round().astype(int)
    data["sales"] = (data["quantity"] * data["unit_price"]).round(2)
    data["order_date"] = data["order_date"].dt.strftime("%Y-%m-%d")
    data = data.sort_values("order_date").reset_index(drop=True)
    audit = {
        "original_rows": original_rows,
        "duplicate_rows_removed": duplicate_count,
        "missing_cells_before_cleaning": missing_before,
        "outliers_flagged_by_iqr": outlier_counts,
        "rows_removed_for_invalid_dates": invalid_dates,
        "final_rows": len(data),
        "missing_cells_after_cleaning": int(data.isna().sum().sum()),
    }
    return data, audit


def create_visuals(cleaned):
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    data = cleaned.copy()
    data["order_date"] = pd.to_datetime(data["order_date"])
    data["month"] = data["order_date"].dt.to_period("M").astype(str)
    product_sales = data.groupby("product")["sales"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(product_sales.index, product_sales.values)
    ax.set(title="Total Sales by Product", xlabel="Sales (INR)", ylabel="Product")
    fig.tight_layout(); fig.savefig(CHART_DIR / "sales_by_product.png", dpi=160); plt.close(fig)
    monthly = data.groupby("month", as_index=False)["sales"].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly["month"], monthly["sales"], marker="o")
    ax.set(title="Monthly Sales Trend", xlabel="Month", ylabel="Sales (INR)")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout(); fig.savefig(CHART_DIR / "monthly_sales_trend.png", dpi=160); plt.close(fig)
    region_sales = data.groupby("region")["sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(region_sales.index, region_sales.values)
    ax.set(title="Total Sales by Region", xlabel="Region", ylabel="Sales (INR)")
    fig.tight_layout(); fig.savefig(CHART_DIR / "sales_by_region.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(data["quantity"], bins=12)
    ax.set(title="Order Quantity Distribution", xlabel="Quantity", ylabel="Number of Orders")
    fig.tight_layout(); fig.savefig(CHART_DIR / "quantity_distribution.png", dpi=160); plt.close(fig)
    corr = data[["quantity", "unit_price", "customer_rating", "sales"]].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(corr.values, vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(corr.columns)), labels=corr.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(corr.index)), labels=corr.index)
    for i in range(len(corr.index)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Numeric Feature Correlations")
    fig.tight_layout(); fig.savefig(CHART_DIR / "correlation_heatmap.png", dpi=160); plt.close(fig)


def write_report(cleaned, audit):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    data = cleaned.copy()
    data["order_date"] = pd.to_datetime(data["order_date"])
    monthly = data.assign(month=data["order_date"].dt.to_period("M").astype(str)).groupby("month")["sales"].sum()
    lines = [
        "DATA CLEANING & VISUALIZATION — QUALITY REPORT", "=" * 52, "",
        "DATA QUALITY AUDIT",
        f"Original rows: {audit['original_rows']}",
        f"Duplicate rows removed: {audit['duplicate_rows_removed']}",
        f"Missing cells before cleaning: {audit['missing_cells_before_cleaning']}",
        f"Rows removed for invalid dates: {audit['rows_removed_for_invalid_dates']}",
        f"Final rows: {audit['final_rows']}",
        f"Missing cells after cleaning: {audit['missing_cells_after_cleaning']}",
        "", "IQR OUTLIERS FLAGGED",
    ]
    lines.extend(f"  {k}: {v}" for k, v in audit["outliers_flagged_by_iqr"].items())
    lines += [
        "", "KEY FINDINGS",
        f"Total sales: INR {data['sales'].sum():,.2f}",
        f"Average order value: INR {data['sales'].mean():,.2f}",
        f"Top product by sales: {data.groupby('product')['sales'].sum().idxmax()}",
        f"Top region by sales: {data.groupby('region')['sales'].sum().idxmax()}",
        f"Best month by sales: {monthly.idxmax()}",
        "", "See reports/charts/ for five generated visualizations.",
        "Note: sample dataset is synthetic; interpret findings as a demonstration."
    ]
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    raw = load_data(RAW_FILE)
    cleaned, audit = clean_data(raw)
    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEAN_FILE, index=False)
    create_visuals(cleaned)
    write_report(cleaned, audit)
    print("Project completed successfully.")
    print(f"Cleaned dataset: {CLEAN_FILE}")
    print(f"Quality report: {REPORT_FILE}")
    print(f"Charts folder: {CHART_DIR}")


if __name__ == "__main__":
    main()
