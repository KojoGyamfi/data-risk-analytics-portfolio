import streamlit as st
import pandas as pd
import altair as alt
import os

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join("data", "explained_pnl_timeseries.csv"), parse_dates=["date"])
    df["long_short"] = df["position"].apply(lambda x: "Long" if x > 0 else "Short")
    return df

df = load_data()

st.title("📈 Multi-Day P&L Attribution Dashboard")

# Sidebar filters
st.sidebar.header("🔍 Filters")
group_key = st.sidebar.selectbox("Group by", ["ticker", "sector", "region", "long_short"])
date_range = st.sidebar.date_input(
    "Select date range",
    [df["date"].min(), df["date"].max()],
    min_value=df["date"].min(),
    max_value=df["date"].max()
)

# Filter data
mask = (df["date"] >= pd.to_datetime(date_range[0])) & (df["date"] <= pd.to_datetime(date_range[1]))
filtered_df = df[mask]

# Grouped summary
grouped = (
    filtered_df.groupby(["date", group_key])
    .agg({
        "actual_pnl": "sum",
        "explained_pnl": "sum",
        "residual": "sum",
        "delta_pnl": "sum",
        "gamma_pnl": "sum",
        "vega_pnl": "sum",
        "theta_pnl": "sum"
    })
    .reset_index()
)

# === Section 1: Table - Daily Actual vs Explained PnL ===
st.subheader(f"📊 Daily Actual vs Explained P&L by {group_key}")

summary_df = grouped[["date", group_key, "actual_pnl", "explained_pnl", "residual"]].copy()
summary_df = summary_df.sort_values("date", ascending=False)
summary_df[["actual_pnl", "explained_pnl", "residual"]] = summary_df[
    ["actual_pnl", "explained_pnl", "residual"]
].round(2)

st.dataframe(summary_df, use_container_width=True)

# === Section 2: Table - Greek Breakdown ===
st.subheader(f"🧮 Daily Greek Attribution by {group_key}")

greek_df = grouped[["date", group_key, "delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl"]].copy()
greek_df = greek_df.sort_values("date", ascending=False)
greek_df[["delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl"]] = greek_df[
    ["delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl"]
].round(2)

st.dataframe(greek_df, use_container_width=True)

# === Section 3: Area Chart - Greek Attribution Over Time ===
st.subheader(f"📉 Stacked Area Chart of Greek Attribution by {group_key}")

area_chart = alt.Chart(grouped).transform_fold(
    ["delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl"],
    as_=["Greek", "value"]
).mark_area(opacity=0.7).encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y("value:Q", title="P&L"),
    color=alt.Color("Greek:N", title="Greek"),
    tooltip=["date:T", "Greek:N", "value:Q"],
    facet=alt.Facet(f"{group_key}:N", columns=3, title=None)
).properties(width=250, height=200)

st.altair_chart(area_chart, use_container_width=True)
