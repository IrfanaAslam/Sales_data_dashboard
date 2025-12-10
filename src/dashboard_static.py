# src/dashboard_static.py
import matplotlib.pyplot as plt
import seaborn as sns
from analytics import load_and_prepare, kpis, monthly_revenue, top_products, revenue_by_region, category_share, monthly_pivot
import pandas as pd

def create_static_dashboard(data_path: str, out_path="sales_dashboard_portfolio.png"):
    df = load_and_prepare(data_path)
    KP = kpis(df)
    ts = monthly_revenue(df)
    top5 = top_products(df, n=5)
    reg = revenue_by_region(df)
    cat = category_share(df)
    pivot = monthly_pivot(df)

    sns.set_style("whitegrid")
    fig = plt.figure(constrained_layout=True, figsize=(14,10))
    gs = fig.add_gridspec(3, 4)

    # KPI panel (full width top)
    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.axis('off')
    kpi_text = (f"Total Revenue: ${KP['total_revenue']:,.0f}    |    Orders: {KP['total_orders']}    |    "
                f"Avg Order: ${KP['avg_order_value']:,.2f}    |    Top Product: {KP['top_product']}    |    Top Region: {KP['top_region']}")
    ax_kpi.text(0.5, 0.5, kpi_text, ha='center', va='center', fontsize=12, fontweight='bold', color='#222')

    # Time series
    ax_ts = fig.add_subplot(gs[1, :2])
    ax_ts.plot(ts.index, ts.values, marker='o', linewidth=2)
    ma = ts.rolling(3, min_periods=1).mean()
    ax_ts.plot(ma.index, ma.values, linestyle='--', alpha=0.8)
    ax_ts.set_title("Monthly Revenue")
    ax_ts.tick_params(axis='x', rotation=45)

    # Top products
    ax_top = fig.add_subplot(gs[1, 2:])
    ax_top.barh(top5.index[::-1], top5.values[::-1], color=sns.color_palette("viridis", len(top5)))
    ax_top.set_title("Top Products")
    for i, v in enumerate(top5.values[::-1]):
        ax_top.text(v + max(top5.values)*0.02, i, f"${v:,.0f}", va='center')

    # Heatmap product vs month
    ax_heat = fig.add_subplot(gs[2, :2])
    if not pivot.empty:
        sns.heatmap(pivot, ax=ax_heat, cmap="YlGnBu", cbar_kws={'label':'Revenue'})
    ax_heat.set_title("Product x Month Revenue (heatmap)")

    # Region pie
    ax_reg = fig.add_subplot(gs[2, 2])
    ax_reg.pie(reg.values, labels=reg.index, autopct='%1.1f%%', startangle=140, pctdistance=0.8)
    ax_reg.set_title("Revenue by Region")

    # Category donut
    ax_cat = fig.add_subplot(gs[2, 3])
    wedges, texts, autotexts = ax_cat.pie(cat.values, labels=cat.index, autopct='%1.1f%%', startangle=140)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    ax_cat.set_title("Revenue by Category")

    plt.suptitle("Sales Data Dashboard — Portfolio Export", fontsize=16, fontweight='bold', y=0.99)
    fig.savefig(out_path, dpi=300)
    print(f"Saved static dashboard → {out_path}")

if __name__ == "__main__":
    create_static_dashboard("data/sample_sales_data.csv")
