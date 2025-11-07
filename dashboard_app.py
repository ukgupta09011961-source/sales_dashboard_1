import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard")
st.write("Analyze your daily product performance interactively!")

# Load data (same folder)
try:
    df = pd.read_csv("sales_data.csv")
except FileNotFoundError:
    st.error("sales_data.csv not found in this folder. Create it and rerun.")
    st.stop()

# Normalize column names
df.columns = [c.strip() for c in df.columns]

# Ensure expected columns exist
expected = {"Date", "Product", "Quantity", "Price"}
if not expected.issubset(set(df.columns)):
    st.error(f"CSV missing columns. Expected: {expected}. Found: {list(df.columns)}")
    st.stop()

# Compute Revenue
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0).astype(int)
df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
df["Revenue"] = df["Quantity"] * df["Price"]

# Sidebar filters
st.sidebar.header("🔍 Filter Data")
products = st.sidebar.multiselect(
    "Select Products:",
    sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique())
)

# Date filter
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
min_date = df["Date"].min()
max_date = df["Date"].max()
date_range = st.sidebar.date_input("Date range", value=(min_date.date(), max_date.date()))
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

# Apply filters
filtered_df = df[
    (df["Product"].isin(products)) &
    (df["Date"] >= start_date) &
    (df["Date"] <= end_date)
]

# Summary and table
st.subheader("📅 Summary Data")
st.dataframe(filtered_df.reset_index(drop=True))

total_rev = filtered_df["Revenue"].sum()
st.metric(label="💰 Total Revenue", value=f"₹{total_rev:,.2f}")

# Visualizations
st.subheader("📈 Revenue by Product")
fig, ax = plt.subplots(figsize=(7, 4))
sns.barplot(data=filtered_df, x="Product", y="Revenue", ci=None, ax=ax)
ax.set_title("Revenue by Product")
ax.set_xlabel("")
st.pyplot(fig)

st.subheader("📅 Daily Revenue Trend")
daily_rev = filtered_df.groupby(filtered_df["Date"].dt.date)["Revenue"].sum().reset_index()
if not daily_rev.empty:
    st.line_chart(daily_rev.set_index("Date"))
else:
    st.info("No data in selected filters to plot.")
