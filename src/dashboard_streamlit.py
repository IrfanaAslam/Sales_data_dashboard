# src/dashboard_streamlit.py
import streamlit as st
import pandas as pd
import io
from analytics import (
    load_and_prepare,
    kpis,
    monthly_revenue,
    top_products,
    revenue_by_region,
    category_share,
    monthly_pivot,
    top_products_by_region,
    auto_insights,
    percent_change
)
import plotly.express as px
import plotly.graph_objects as go
from dashboard_static import create_static_dashboard


from pathlib import Path

DATA_PATH = "data/sample_sales_data.csv"

st.set_page_config(page_title="Sales Data Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("📊 Sales Data Dashboard — Advanced")

# Load
df = load_and_prepare(DATA_PATH)

# Sidebar filters
st.sidebar.header("Filters")
years = sorted(df['Year'].unique(), reverse=True)
sel_year = st.sidebar.selectbox("Year", options=years, index=0)
regions = ["All"] + sorted(df['Region'].unique())
sel_regions = st.sidebar.multiselect("Region (choose one or more)", options=regions, default=["All"])

if "All" in sel_regions:
    filtered = df[df['Year'] == sel_year]
else:
    filtered = df[(df['Year'] == sel_year) & (df['Region'].isin(sel_regions))]

# KPIs
KP = kpis(filtered)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${KP['total_revenue']:,.0f}")
col2.metric("Total Orders", f"{KP['total_orders']}")
col3.metric("Avg Order Value", f"${KP['avg_order_value']:,.2f}")
col4.metric("Top Product", KP['top_product'])

# Delta KPIs vs previous year (if present)
prev = df[df['Year'] == (sel_year - 1)]
if not prev.empty:
    prev_kp = kpis(prev)
    delta_revenue = percent_change(KP['total_revenue'], prev_kp['total_revenue'])
    if delta_revenue is not None:
        st.metric(label="Revenue Δ YoY", value=f"{delta_revenue:+.1f}%", delta=f"{delta_revenue:+.1f}%")

st.markdown("---")

# Auto Insights
ins = auto_insights(df)
if ins:
    st.markdown("### 🔎 Automated Insights")
    for i in ins:
        st.markdown(f"- {i}")
    st.markdown("---")

# Charts layout
left, right = st.columns((2,1))

# Time series (left)
with left:
    st.subheader("Monthly Revenue")
    ts = monthly_revenue(filtered)
    if ts.empty:
        st.write("No data for selected filters.")
    else:
        fig = px.line(x=ts.index, y=ts.values, labels={'x':'Month','y':'Revenue'}, markers=True)
        fig.add_trace(go.Scatter(x=ts.index, y=ts.rolling(3).mean(), mode='lines', name='3-month MA', line=dict(dash='dash')))
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap product x month
    st.subheader("Product vs Month Heatmap")
    pivot = monthly_pivot(filtered)
    if not pivot.empty:
        fig2 = px.imshow(pivot.fillna(0), labels=dict(x="Month", y="Product", color="Revenue"), aspect="auto")
        st.plotly_chart(fig2, use_container_width=True)

# Right column charts
with right:
    st.subheader("Top Products")
    tp = top_products(filtered, n=10).reset_index()
    if tp.empty:
        st.write("No data")
    else:
        fig3 = px.bar(tp, x='Revenue', y='Product', orientation='h', text='Revenue', color='Revenue', color_continuous_scale='Blues')
        fig3.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
        fig3.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0))
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Revenue by Region")
    reg = revenue_by_region(filtered).reset_index()
    if not reg.empty:
        fig4 = px.pie(reg, names='Region', values='Revenue', hole=0.45)
        st.plotly_chart(fig4, use_container_width=True)

# Top products by selected region (extra)
st.subheader("Top Products by Region")
sel_region_for_top = st.selectbox("Choose region", options=list(filtered['Region'].unique()))
if sel_region_for_top:
    tpr = top_products_by_region(filtered, sel_region_for_top, n=5)
    if not tpr.empty:
        st.table(tpr.reset_index().rename(columns={'Revenue':'Revenue ($)'}))

st.markdown("---")
# Downloads
st.subheader("Export & Download")

# Download filtered data CSV
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button("Download filtered data (CSV)", data=csv, file_name="filtered_sales.csv", mime="text/csv")

# Create static portfolio PNG for current filtered dataset (calls static generator)
if st.button("Generate portfolio PNG (high-res)"):
    tmp_out = "sales_dashboard_portfolio.png"
    # Save filtered dataset temporarily
    tmp_path = "data/tmp_filtered.csv"
    filtered.to_csv(tmp_path, index=False)
    # Use static generator with that file
    try:
        create_static_dashboard(tmp_path, out_path=tmp_out)
        with open(tmp_out, "rb") as f:
            st.download_button("Download generated PNG", data=f, file_name=tmp_out, mime="image/png")
    except Exception as e:
        st.error(f"Export failed: {e}")

st.caption("Tip: Use the filters, then click 'Generate portfolio PNG' to export a snapshot of the current view.")
