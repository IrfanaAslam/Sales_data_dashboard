# src/analytics.py
import pandas as pd
import numpy as np

def load_and_prepare(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date']).copy()
    for col in ['UnitPrice','Quantity','Revenue']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df

def kpis(df: pd.DataFrame, freq='M'):
    total_revenue = df['Revenue'].sum()
    total_orders = df['OrderID'].nunique() if 'OrderID' in df.columns else len(df)
    avg_order_value = total_revenue / (total_orders or 1)
    top_product = df.groupby('Product')['Revenue'].sum().idxmax()
    top_region = df.groupby('Region')['Revenue'].sum().idxmax()
    return {
        "total_revenue": float(total_revenue),
        "total_orders": int(total_orders),
        "avg_order_value": float(avg_order_value),
        "top_product": top_product,
        "top_region": top_region
    }

def monthly_revenue(df: pd.DataFrame):
    ts = df.groupby(df['Month'])['Revenue'].sum().sort_index()
    return ts

def top_products(df: pd.DataFrame, n=10):
    return df.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(n)

def revenue_by_region(df: pd.DataFrame):
    return df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)

def category_share(df: pd.DataFrame):
    return df.groupby('Category')['Revenue'].sum().sort_values(ascending=False)

def monthly_pivot(df: pd.DataFrame):
    # pivot product x month revenue (for heatmap)
    pivot = df.pivot_table(values='Revenue', index='Product', columns=df['Month'].dt.strftime('%Y-%m'), aggfunc='sum', fill_value=0)
    return pivot

def top_products_by_region(df: pd.DataFrame, region, n=5):
    sub = df[df['Region'] == region]
    return sub.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(n)

def percent_change(current: float, previous: float):
    if previous == 0:
        return None
    return (current - previous) / previous * 100.0

def auto_insights(df: pd.DataFrame):
    insights = []
    try:
        # top product change month over month
        monthly = df.groupby([df['Month'].dt.to_period('M'),'Product'])['Revenue'].sum().unstack(fill_value=0)
        months = monthly.index.sort_values()
        if len(months) >= 2:
            last, prev = months[-1], months[-2]
            last_s = monthly.loc[last]
            prev_s = monthly.loc[prev]
            top_last = last_s.idxmax()
            change = percent_change(last_s[top_last], prev_s.get(top_last, 0))
            if change is not None:
                insights.append(f"Top product in {last.strftime('%b %Y')} was **{top_last}** with revenue ${last_s[top_last]:,.0f} ({change:+.1f}% vs previous month).")
        # region share
        region = df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
        if not region.empty:
            top_reg = region.index[0]
            insights.append(f"Top region: **{top_reg}** contributing {region.iloc[0]/region.sum()*100:.1f}% of total revenue.")
        # fastest growing product last 3 months
        monthly_total = df.groupby([df['Month'].dt.to_period('M'),'Product'])['Revenue'].sum().unstack(fill_value=0)
        if monthly_total.shape[0] >= 4:
            last3 = monthly_total.iloc[-3:].sum()
            prev3 = monthly_total.iloc[-6:-3].sum()
            growth = ((last3 - prev3) / (prev3.replace(0, np.nan))).replace([np.inf, -np.inf], np.nan)
            growth = growth.dropna().sort_values(ascending=False)
            if not growth.empty:
                prod = growth.index[0]
                insights.append(f"Fastest growing product (last 3 months vs previous 3 months): **{prod}** (+{growth.iloc[0]:.1%}).")
    except Exception:
        pass
    return insights
