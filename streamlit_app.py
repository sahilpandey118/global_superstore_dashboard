import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Global Superstore Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
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

st.title("📊 Global Superstore – Interactive Dashboard")

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Filters")
segments = st.sidebar.multiselect(
    "Select Segment(s)",
    options=sorted(df["Segment"].unique()),
    default=sorted(df["Segment"].unique())
)
categories = st.sidebar.multiselect(
    "Select Category(s)",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)
regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

df_filtered = df[
    df["Segment"].isin(segments)
    & df["Category"].isin(categories)
    & df["Region"].isin(regions)
]

# ---------------- KPIs ----------------
total_sales = df_filtered["Sales"].sum()
total_profit = df_filtered["Profit"].sum()
num_orders = df_filtered["Order ID"].nunique()
num_customers = df_filtered["Customer ID"].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"${total_sales:,.0f}")
k2.metric("Total Profit", f"${total_profit:,.0f}")
k3.metric("Orders", f"{num_orders:,}")
k4.metric("Customers", f"{num_customers:,}")

st.markdown("---")

# ---------------------------------------------------------
# Q1. Monthly Sales Trend
st.subheader("Q1. How have total sales evolved over time?")
monthly = (
    df_filtered.groupby("Order Month Name")["Sales"]
    .sum()
    .reset_index()
    .sort_values("Order Month Name")
)
if not monthly.empty:
    fig1 = px.line(monthly, x="Order Month Name", y="Sales", title="Monthly Sales Trend")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No data for selected filters.")

# ---------------------------------------------------------
# Q2. Sales and Profit by Category
st.subheader("Q2. Which product categories generate the highest sales and profit?")
cat_perf = (
    df_filtered.groupby("Category")[["Sales", "Profit"]]
    .sum()
    .sort_values("Sales", ascending=False)
    .reset_index()
)
if not cat_perf.empty:
    fig2 = px.bar(cat_perf, x="Category", y=["Sales", "Profit"], barmode="group",
                  title="Sales and Profit by Category")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No data for selected filters.")

# ---------------------------------------------------------
# Q3. Sub-category Performance
st.subheader("Q3. Which sub-categories contribute most to total sales?")
subcat_sales = (
    df_filtered.groupby(["Category", "Sub-Category"])["Sales"]
    .sum()
    .reset_index()
    .sort_values("Sales", ascending=False)
)
if not subcat_sales.empty:
    fig3 = px.bar(subcat_sales, x="Sub-Category", y="Sales", color="Category",
                  title="Sales by Sub-Category within Each Category")
    fig3.update_xaxes(tickangle=45)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No data for selected filters.")

# ---------------------------------------------------------
# Q4. Regional and Market Performance
st.subheader("Q4. How do different regions and markets perform in terms of total sales?")
region_sales = (
    df_filtered.groupby(["Market", "Region"])["Sales"]
    .sum()
    .reset_index()
)
if not region_sales.empty:
    fig4 = px.bar(region_sales, x="Region", y="Sales", color="Market",
                  title="Sales by Region and Market")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No data for selected filters.")

# ---------------------------------------------------------
# Q5. Top 10 Customers
st.subheader("Q5. Who are the top 10 customers by total purchase value?")
top_customers = (
    df_filtered.groupby("Customer Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
if not top_customers.empty:
    fig5 = px.bar(top_customers, x="Sales", y="Customer Name", orientation="h",
                  title="Top 10 Customers by Total Sales")
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("No data for selected filters.")

# ---------------------------------------------------------
# Q6. Order Value Distribution
st.subheader("Q6. What is the distribution of order values?")
order_sales = df_filtered.groupby("Order ID")["Sales"].sum().reset_index()
if not order_sales.empty:
    fig6 = px.histogram(order_sales, x="Sales", nbins=50,
                        title="Distribution of Order Values (per Order)")
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("No order data for selected filters.")

# ---------------------------------------------------------
# Q7. Sales by Day of Week
st.subheader("Q7. On which day of the week are the most sales recorded?")
dow_sales = (
    df_filtered.groupby("Order Day of Week")["Sales"]
    .sum()
    .reindex(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )
    .reset_index()
)
if not dow_sales.empty:
    fig7 = px.bar(dow_sales, x="Order Day of Week", y="Sales",
                  title="Sales by Day of Week")
    st.plotly_chart(fig7, use_container_width=True)
else:
    st.info("No data for selected filters.")

# ---------------------------------------------------------
# Q8. Shipping Mode vs Delivery Time & Cost
st.subheader("Q8. How does shipping mode affect delivery time and cost?")
if not df_filtered.empty:
    c1, c2 = st.columns(2)
    with c1:
        fig8a = px.box(df_filtered, x="Ship Mode", y="Delivery Days",
                       title="Delivery Days by Ship Mode")
        st.plotly_chart(fig8a, use_container_width=True)
    with c2:
        fig8b = px.bar(df_filtered, x="Ship Mode", y="Shipping Cost",
                       title="Average Shipping Cost by Ship Mode", color="Ship Mode",
                       hover_data=["Shipping Cost"])
        st.plotly_chart(fig8b, use_container_width=True)
else:
    st.info("No shipping data for selected filters.")

# ---------------------------------------------------------
# Q9. Discount vs Profit
st.subheader("Q9. How do discounts impact profit?")
if not df_filtered.empty:
    fig9 = px.scatter(df_filtered, x="Discount", y="Profit", color="Category",
                      title="Discount vs Profit")
    st.plotly_chart(fig9, use_container_width=True)
else:
    st.info("No discount data for selected filters.")

# ---------------------------------------------------------
# Q10. Sales by Customer Segment
st.subheader("Q10. What is the sales distribution across customer segments?")
segment_sales = (
    df_filtered.groupby("Segment")["Sales"]
    .sum()
    .reset_index()
)
if not segment_sales.empty:
    fig10 = px.pie(segment_sales, names="Segment", values="Sales",
                   title="Sales Distribution by Customer Segment", hole=0.3)
    st.plotly_chart(fig10, use_container_width=True)
else:
    st.info("No segment data for selected filters.")

# ---------------------------------------------------------
st.caption("Dashboard includes all 10 analytical questions from Colab notebook.")