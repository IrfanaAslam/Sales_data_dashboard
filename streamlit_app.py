"""
streamlit_app.py
Simple Streamlit interactive dashboard to explore the sales dataset.

Run: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
from dashboard import load_and_clean, time_series_summary, top_products, region_summary, category_distribution
import matplotlib.pyplot as plt

DATA_PATH = r"C:\Users\hp\OneDrive\Desktop\Portfolio Projects\Sales_data_dashboaed\data\sample_sales_data.csv"

st.set_page_config(page_title="Sales Dashboard (Streamlit)", layout="wide")
st.title("Sales Dashboard — Interactive")

@st.cache_data
def load_df(path):
    return load_and_clean(pd.io.common.Path(path) if isinstance(path, str) else path)

df = load_df(DATA_PATH)

# Sidebar filters
st.sidebar.header("Filters")
years = sorted(df['Year'].unique())
sel_year = st.sidebar.selectbox("Year", options=years, index=len(years)-1)
regions = ["All"] + sorted(df['Region'].unique().tolist())
sel_region = st.sidebar.selectbox("Region", options=regions)

filtered = df[df['Year'] == sel_year]
if sel_region != "All":
    filtered = filtered[filtered['Region'] == sel_region]

st.subheader(f"Summary — {sel_year} {'' if sel_region=='All' else '— ' + sel_region}")
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${filtered['Revenue'].sum():,.2f}")
col2.metric("Orders", filtered['OrderID'].nunique() if 'OrderID' in filtered.columns else len(filtered))
col3.metric("Average Order Value", f"${filtered['Revenue'].sum()/(filtered['OrderID'].nunique() if 'OrderID' in filtered.columns else (len(filtered) or 1)):.2f}")

# Plots
ts = time_series_summary(filtered)
fig1, ax1 = plt.subplots(figsize=(9,3))
ax1.plot(ts.index, ts.values, marker='o')
ax1.set_title("Monthly Revenue")
ax1.tick_params(axis='x', rotation=45)
st.pyplot(fig1)

top = top_products(filtered, n=8)
fig2, ax2 = plt.subplots(figsize=(6,4))
ax2.barh(top['Product'][::-1], top['Revenue'][::-1])
ax2.set_title("Top Products")
st.pyplot(fig2)

st.write("Top 10 salespeople")
st.dataframe(filtered.groupby('Salesperson')['Revenue'].sum().sort_values(ascending=False).reset_index().head(10))
