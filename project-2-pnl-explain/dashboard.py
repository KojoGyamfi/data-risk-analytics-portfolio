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
df["date"] = df["date"].dt.date

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
st.subheader(f"Daily Actual vs Explained P&L by {group_key}")

summary_df = grouped[["date", group_key, "actual_pnl", "explained_pnl", "residual"]].copy()
summary_df = summary_df.sort_values("date", ascending=False)
summary_df[["actual_pnl", "explained_pnl", "residual"]] = summary_df[
    ["actual_pnl", "explained_pnl", "residual"]
].round(2)

# Format column names
colnames = {
    "date": "Date",
    group_key: group_key.replace("_", " ").title(),
    "trade_id": "Trade ID",
    "position": "Position",
    "actual_pnl": "Actual P&L",
    "explained_pnl": "Explained P&L",
    "residual": "Residual",
    "delta_pnl": "Delta P&L",
    "gamma_pnl": "Gamma P&L",
    "vega_pnl": "Vega P&L",
    "theta_pnl": "Theta P&L"
}
summary_df = summary_df.rename(columns=colnames)

st.dataframe(summary_df, use_container_width=True)

# === Section 2: Table - Greek Breakdown ===
st.subheader(f"Daily Greek Attribution by {group_key}")

greek_df = grouped[["date", group_key, "delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl"]].copy()
greek_df = greek_df.sort_values("date", ascending=False)
greek_df[["delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl"]] = greek_df[
    ["delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl"]
].round(2)
greek_df = greek_df.rename(columns=colnames)

st.dataframe(greek_df, use_container_width=True)

# === Section 3: Area Chart - Greek Attribution Over Time ===
st.subheader(f"Stacked Area Chart of Greek Attribution by {group_key}")

area_chart = alt.Chart(grouped).transform_fold(
    ["delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl"],
    as_=["Greek", "value"]
).mark_area(opacity=0.7).encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y("value:Q", title="P&L"),
    color=alt.Color("Greek:N", title="Greek"),
    tooltip=["date:T", "Greek:N", "value:Q"],
).properties(width=250, height=200)

area_chart = area_chart.facet(
    column=alt.Column(f"{group_key}:N", title=None)
)

st.altair_chart(area_chart, use_container_width=True)

# === Section 4: Cumulative P&L Trend ===
st.subheader(f"Cumulative Actual vs Explained P&L by {group_key}")

cumulative_df = (
    grouped
    .sort_values("date")
    .groupby(group_key)
    .apply(lambda d: d.assign(
        cumulative_actual=d["actual_pnl"].cumsum(),
        cumulative_explained=d["explained_pnl"].cumsum()
    ))
    .reset_index(drop=True)
)

melted = cumulative_df.melt(
    id_vars=["date", group_key],
    value_vars=["cumulative_actual", "cumulative_explained"],
    var_name="type",
    value_name="value"
)

melted["type"] = melted["type"].map({
    "cumulative_actual": "Cumulative Actual",
    "cumulative_explained": "Cumulative Explained"
})

cumulative_chart = alt.Chart(melted).mark_line().encode(
    x="date:T",
    y="value:Q",
    color=alt.Color("type:N", scale=alt.Scale(
        domain=["Cumulative Actual", "Cumulative Explained"],
        range=["#1f77b4", "#ff7f0e"]
    )),
    tooltip=["date:T", "type:N", "value:Q"],
).properties(width=250, height=200)

cumulative_chart = cumulative_chart.facet(
    column=alt.Column(f"{group_key}:N", title=None)
)

st.altair_chart(cumulative_chart, use_container_width=True)

# === Section 5: Drilldown Table ===
st.subheader(f"Trade-Level Drilldown by {group_key}")

group_vals = filtered_df[group_key].dropna().unique()
selected_group = st.selectbox(f"Select {group_key.replace('_', ' ').title()} to explore", sorted(group_vals))

drilldown_df = filtered_df[filtered_df[group_key] == selected_group].copy()
cols = [
    "date", "trade_id", "ticker", "position",
    "delta_pnl", "gamma_pnl", "vega_pnl", "theta_pnl",
    "explained_pnl", "actual_pnl", "residual"
]
drilldown_df = drilldown_df[cols].sort_values(["date", "trade_id"])
drilldown_df = drilldown_df.round(2)
drilldown_df = drilldown_df.rename(columns=colnames)

st.dataframe(drilldown_df, use_container_width=True)
