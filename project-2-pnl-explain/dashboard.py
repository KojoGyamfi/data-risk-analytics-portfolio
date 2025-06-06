import streamlit as st
from pnl_model import load_data, compute_attribution, summarize_by_group

st.set_page_config(page_title="P&L Explain Tool", layout="wide")

st.title("📊 P&L Attribution Dashboard")

# Load and compute
positions, market, actuals = load_data()
df = compute_attribution(positions, market, actuals)

# User selection
group_option = st.selectbox("Group P&L by:", ["ticker", "instrument_type"])

# Show summary
summary_df = summarize_by_group(df, groupby_col=group_option)
st.subheader(f"P&L Summary Grouped by {group_option.capitalize()}")
st.dataframe(summary_df, use_container_width=True)

# Optional: download
csv = summary_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Summary CSV", data=csv, file_name="pnl_summary.csv", mime="text/csv")
