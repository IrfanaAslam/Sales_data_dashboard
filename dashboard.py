"""
dashboard.py
Produces a 2x2 matplotlib dashboard PNG and PDF from a sales CSV.

Usage:
    1. Place your data as 'sample_sales_data.csv' in same folder (or change DATA_PATH)
    2. python dashboard.py
Outputs:
    - sales_dashboard.png
    - sales_dashboard.pdf
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Tuple

DATA_PATH = Path("sample_sales_data.csv")
OUT_PNG = Path("sales_dashboard.png")
OUT_PDF = Path("sales_dashboard.pdf")

def load_and_clean(path: Path) -> pd.DataFrame:
    """Load CSV, parse dates, fill/correct columns, add Year/Month columns."""
    df = pd.read_csv(path)
    # Standardize column names
    df.columns = [c.strip() for c in df.columns]
    # Parse Date
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    # Drop rows with invalid date
    df = df.dropna(subset=['Date']).copy()
    # Ensure numeric types
    for col in ['UnitPrice','Quantity','Revenue']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    # If Revenue missing or inconsistent, recalc
    df['Revenue'] = df.apply(
        lambda r: round(r['UnitPrice'] * r['Quantity'], 2)
        if pd.isna(r['Revenue']) or abs(r['Revenue'] - (r['UnitPrice'] * r['Quantity'])) > 0.01
        else r['Revenue'],
        axis=1
    )
    # Add Year, Month
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df

def time_series_summary(df: pd.DataFrame) -> pd.Series:
    """Monthly revenue time series (monthly total)."""
    ts = df.groupby('Month')['Revenue'].sum().sort_index()
    return ts

def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N products by revenue."""
    t = df.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(n).reset_index()
    return t

def region_summary(df: pd.DataFrame) -> pd.Series:
    """Revenue by region."""
    return df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)

def category_distribution(df: pd.DataFrame) -> pd.Series:
    """Category share (for pie chart)."""
    return df.groupby('Category')['Revenue'].sum().sort_values(ascending=False)

def moving_average(series: pd.Series, window: int = 3) -> pd.Series:
    return series.rolling(window=window, min_periods=1, center=False).mean()

def plot_dashboard(ts: pd.Series, top_prod: pd.DataFrame, region_s: pd.Series, cat_s: pd.Series, out_png: Path, out_pdf: Path):
    """Create a 2x2 dashboard and save to PNG and PDF."""
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    # --- Line chart: Monthly revenue + moving average
    ax = axes[0,0]
    ax.plot(ts.index, ts.values, marker='o', linewidth=2, label='Monthly Revenue')
    ma = moving_average(ts, window=3)
    ax.plot(ma.index, ma.values, linestyle='--', marker='s', label='3-month MA')
    ax.set_title("Monthly Revenue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    ax.grid(alpha=0.25)
    ax.legend()
    for label in ax.get_xticklabels():
        label.set_rotation(45)
    # --- Bar chart: Top products
    ax = axes[0,1]
    ax.barh(top_prod['Product'][::-1], top_prod['Revenue'][::-1])  # horizontal, descending
    ax.set_title("Top Products by Revenue (Top {})".format(len(top_prod)))
    ax.set_xlabel("Revenue")
    ax.grid(axis='x', alpha=0.2)
    # --- Bar chart: Region performance
    ax = axes[1,0]
    region_s.plot(kind='bar', ax=ax)
    ax.set_title("Revenue by Region")
    ax.set_ylabel("Revenue")
    ax.set_xlabel("")
    ax.grid(axis='y', alpha=0.2)
    # --- Pie chart: Category distribution
    ax = axes[1,1]
    # If many categories, group small into 'Other'
    if len(cat_s) > 6:
        top = cat_s.head(6)
        others = cat_s.iloc[6:].sum()
        pie_series = top.append(pd.Series({'Other': others}))
    else:
        pie_series = cat_s
    ax.pie(pie_series.values, labels=pie_series.index, autopct='%1.1f%%', startangle=140)
    ax.set_title("Revenue by Category (share)")
    # Layout & save
    plt.suptitle("Sales Dashboard — Generated on {}".format(datetime.now().strftime("%Y-%m-%d %H:%M")), fontsize=14, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_png, dpi=150)
    fig.savefig(out_pdf)
    print(f"Saved dashboard to {out_png.resolve()} and {out_pdf.resolve()}")
    plt.close(fig)

def summary_text(df: pd.DataFrame) -> str:
    """Return a small textual summary (top-level KPIs)."""
    total_revenue = df['Revenue'].sum()
    num_orders = df['OrderID'].nunique() if 'OrderID' in df.columns else len(df)
    top_product = df.groupby('Product')['Revenue'].sum().idxmax()
    top_region = df.groupby('Region')['Revenue'].sum().idxmax()
    return (f"Total revenue: ${total_revenue:,.2f}\n"
            f"Orders: {num_orders}\n"
            f"Top product: {top_product}\n"
            f"Top region: {top_region}\n")

def main():
    if not DATA_PATH.exists():
        raise SystemExit(f"Data file not found: {DATA_PATH}. Run generate_sample_data.py first or point DATA_PATH to your CSV.")
    df = load_and_clean(DATA_PATH)
    print("Loaded data rows:", len(df))
    print(summary_text(df))
    ts = time_series_summary(df)
    tp = top_products(df, n=10)
    rs = region_summary(df)
    cs = category_distribution(df)
    plot_dashboard(ts, tp, rs, cs, OUT_PNG, OUT_PDF)

if __name__ == "__main__":
    main()
