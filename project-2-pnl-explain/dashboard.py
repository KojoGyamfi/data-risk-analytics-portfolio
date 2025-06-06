import streamlit as st
import pandas as pd
import altair as alt
import os

# Load data
@st.cache_data
def load_data():
    path = os.path.join("data", "explained_pnl_timeseries.csv")
    df = pd.read_csv(path, parse_dates=["date"])
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

# Filtered data
mask = (df["date"] >= pd.to_datetime(date_range[0])) & (df["date"] <= pd.to_datetime(date_range[1]))
filtered_df = df[mask]

# Grouped summary
grouped = (
    filtered_df.groupby(["date", group_key])
    .agg({
        "explained_pnl": "sum",
        "actual_pnl": "sum",
        "delta_pnl": "sum",
        "gamma_pnl": "sum",
        "vega_pnl": "sum",
        "theta_pnl": "sum",
        "residual": "sum"
    })
    .reset_index()
)

# Line chart
st.subheader(f"📅 Daily Actual vs Explained P&L by {group_key}")
line_chart = alt.Chart(grouped).mark_line().encode(
    x="date:T",
    y=alt.Y("value:Q", title="P&L"),
    color="metric:N",
    tooltip=["date:T", group_key, "value:Q"]
).transform_fold(
    ["actual_pnl", "explained_pnl"],
    as_=["metric", "value"]
).properties(width=800, height=400)

st.altair_chart(line_chart, use_container_width=True)

# Greek chart
st.subheader(f"📊 Daily Greek Breakdown by {group_key}")
greek_chart = alt.Chart(grouped).transform_fold(
    ["delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl"],
    as_=["Greek", "value"]
).mark_bar().encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y("value:Q", title="P&L"),
    color=alt.Color("Greek:N", title="Greek"),
    column=alt.Column(f"{group_key}:N", title=group_key.capitalize()),
    tooltip=["Greek:N", "value:Q"]
).properties(width=150)

st.altair_chart(greek_chart, use_container_width=True)


# Heatmap
st.subheader(f"🧯 Residual P&L Heatmap by {group_key} and Date")
heatmap = alt.Chart(grouped).mark_rect().encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y(f"{group_key}:N", title=group_key.capitalize()),
    color=alt.Color("residual:Q", scale=alt.Scale(scheme="redblue"), title="Residual"),
    tooltip=["date:T", group_key, "residual:Q"]
).properties(width=800, height=400)

st.altair_chart(heatmap, use_container_width=True)
