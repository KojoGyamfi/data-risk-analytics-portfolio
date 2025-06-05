import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from io import BytesIO

# Page Setup
st.set_page_config(page_title="Real Portfolio VaR Dashboard", layout="wide")
st.title("📊 Daily VaR & Risk Dashboard – Real Portfolio")

# Sidebar Inputs
st.sidebar.header("Portfolio Configuration")
tickers = st.sidebar.multiselect(
    "Select Assets (max 5):",
    ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'META', 'JPM', 'NVDA', 'XOM', 'BP'],
    default=['AAPL', 'MSFT', 'GOOGL']
)

weights = {}
for ticker in tickers:
    weights[ticker] = st.sidebar.slider(f"{ticker} Weight", 0.0, 1.0, 0.33, 0.01)
total_weight = sum(weights.values())
weights = {k: v / total_weight for k, v in weights.items()}

confidence_level = st.sidebar.selectbox("Confidence Level", [0.95, 0.99])
vol_window = st.sidebar.slider("Rolling Volatility Window", 10, 60, 20)
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-31"))

# Data Fetching
data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
returns = data.pct_change().dropna()
returns['Portfolio'] = sum(returns[ticker] * weight for ticker, weight in weights.items())

# Risk Metrics
def calculate_var(series, confidence=0.95):
    return -np.percentile(series, (1 - confidence) * 100)

def calculate_es(series, confidence=0.95):
    threshold = np.percentile(series, (1 - confidence) * 100)
    return -series[series <= threshold].mean()

latest_var = calculate_var(returns['Portfolio'], confidence=confidence_level)
latest_es = calculate_es(returns['Portfolio'], confidence=confidence_level)
rolling_vol = returns['Portfolio'].rolling(vol_window).std()

# Export Report
def convert_df_to_csv(df):
    return df.to_csv(index=True).encode('utf-8')

report_df = pd.DataFrame({
    "Metric": ["VaR", "Expected Shortfall", "Annualized Volatility"],
    "Value": [f"{latest_var:.2%}", f"{latest_es:.2%}", f"{rolling_vol.iloc[-1]*np.sqrt(252):.2%}"]
})

csv = convert_df_to_csv(report_df)

# Dashboard Display
st.subheader("🔐 Portfolio Risk Summary")
st.metric(label=f"{int(confidence_level*100)}% 1-Day VaR", value=f"{latest_var:.2%}")
st.metric(label=f"{int(confidence_level*100)}% Expected Shortfall", value=f"{latest_es:.2%}")
st.metric(label="Annualized Volatility", value=f"{rolling_vol.iloc[-1]*np.sqrt(252):.2%}")

if latest_var > 0.03:
    st.warning("⚠️ VaR exceeds 3% threshold — review portfolio risk exposure!")

st.download_button("📥 Download Risk Summary (CSV)", data=csv, file_name="risk_report.csv", mime='text/csv')

st.subheader("📉 Rolling Volatility")
st.line_chart(rolling_vol)

st.subheader("📈 Return Distribution")
fig, ax = plt.subplots()
returns['Portfolio'].hist(bins=50, ax=ax, color='skyblue', edgecolor='black')
ax.axvline(-latest_var, color='red', linestyle='--', label='VaR Threshold')
ax.axvline(-latest_es, color='orange', linestyle='--', label='ES Threshold')
ax.set_title('Distribution of Daily Portfolio Returns')
ax.legend()
st.pyplot(fig)
