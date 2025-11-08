import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Superstore Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("Global_Superstore2.csv", encoding="latin1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True, errors="coerce")
    df["Order Month"] = df["Order Date"].dt.to_period("M")
    df["Order Month Name"] = df["Order Date"].dt.strftime("%Y-%m")
    df["Order Day of Week"] = df["Order Date"].dt.day_name()
    df["Delivery Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    return df

df = load_data()

st.title("📊 Global Superstore Sales Dashboard")

st.sidebar.header("Filters")
segments = st.sidebar.multiselect(
    "Segment",
    options=sorted(df["Segment"].unique()),
    default=sorted(df["Segment"].unique())
)
categories = st.sidebar.multiselect(
    "Category",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

df_filtered = df[df["Segment"].isin(segments) & df["Category"].isin(categories)]

# KPIs
total_sales = df_filtered["Sales"].sum()
total_profit = df_filtered["Profit"].sum()
num_orders = df_filtered["Order ID"].nunique()

c1, c2, c3 = st.columns(3)
c1.metric("Total Sales", f"${total_sales:,.0f}")
c2.metric("Total Profit", f"${total_profit:,.0f}")
c3.metric("Number of Orders", f"{num_orders:,}")

# Monthly sales
monthly = (
    df_filtered.groupby("Order Month Name")["Sales"]
    .sum()
    .reset_index()
    .sort_values("Order Month Name")
)
if not monthly.empty:
    fig1 = px.line(monthly, x="Order Month Name", y="Sales", title="Monthly Sales Trend")
    st.plotly_chart(fig1, width="stretch")

# Category sales
cat_sales = (
    df_filtered.groupby("Category")["Sales"]
    .sum()
    .reset_index()
    .sort_values("Sales", ascending=False)
)
if not cat_sales.empty:
    fig2 = px.bar(cat_sales, x="Category", y="Sales", title="Sales by Category")
    st.plotly_chart(fig2, width="stretch")