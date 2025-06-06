import streamlit as st
from pnl_model import load_data, compute_attribution, summarize_by_group

st.set_page_config(page_title="P&L Explain Tool", layout="wide")
st.title("📊 P&L Attribution Dashboard")

# Load and compute
positions, market, actuals = load_data(data_dir="data")
df = compute_attribution(positions, market, actuals)

# Show raw position-level P&L
st.subheader("🔍 Position-Level P&L Attribution")
st.dataframe(df[[
    'trade_id', 'ticker', 'instrument_type', 'direction', 'position',
    'delta_pnl', 'gamma_pnl', 'vega_pnl', 'theta_pnl',
    'explained_pnl', 'actual_pnl', 'residual'
]].round(2), use_container_width=True)

# Grouping options
group_option = st.selectbox("Group P&L by:", ["ticker", "instrument_type", "direction"])
summary_df = summarize_by_group(df, groupby_col=group_option)

# Show group-level results
st.subheader(f"📂 Group-Level P&L Summary by {group_option.capitalize()}")
st.dataframe(summary_df, use_container_width=True)

# Download
csv = summary_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Group Summary CSV", data=csv, file_name="pnl_summary.csv", mime="text/csv")
