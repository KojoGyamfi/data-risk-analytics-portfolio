
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import norm
from io import BytesIO

# Page Setup
st.set_page_config(page_title="Real Portfolio VaR Dashboard", layout="wide")
st.title("Daily VaR & Risk Dashboard – Real Portfolio")

# Sidebar Inputs
st.sidebar.header("Portfolio Configuration")
tickers = st.sidebar.multiselect(
    "Select Assets (max 5):",
    ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'META', 'JPM', 'NVDA', 'XOM', 'BP'],
    default=['AAPL', 'MSFT', 'GOOGL']
)

if not tickers:
    st.warning("Please select at least one ticker.")
    st.stop()

weights = {}
for ticker in tickers:
    weights[ticker] = st.sidebar.slider(f"{ticker} Weight", 0.0, 1.0, 0.33, 0.01)

total_weight = sum(weights.values())
if total_weight == 0:
    st.warning("Total weight must be greater than 0.")
    st.stop()
elif not 0.99 <= total_weight <= 1.01:
    st.error(f"⚠️ Total weight must sum to 1.00 (100%). Currently: {total_weight:.2f}")
    st.stop()

st.sidebar.subheader("VaR Settings")
var_method = st.sidebar.selectbox(
    "Select Parametric VaR Method",
    ["Full-window percentile", "Rolling-volatility parametric"],
    help="Choose 'Rolling-volatility parametric' to estimate VaR assuming returns are normally distributed and recent volatility represents future risk."
)

confidence_level = st.sidebar.selectbox("Confidence Level", [0.95, 0.99])
vol_window = st.sidebar.slider("Rolling Volatility Window (Days)", 10, 60, 20)
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2025-01-01"))

# Data Fetching 
try:
    data = yf.download(tickers, start=start_date, end=end_date)

    if isinstance(data.columns, pd.MultiIndex):
        if 'Adj Close' in data.columns.levels[0]:
            raw_data = data['Adj Close']
        elif 'Close' in data.columns.levels[0]:
            raw_data = data['Close']
        else:
            st.error("Neither 'Adj Close' nor 'Close' prices found in downloaded data.")
            st.stop()
    else:
        if 'Adj Close' in data.columns:
            raw_data = data[['Adj Close']].copy()
        elif 'Close' in data.columns:
            raw_data = data[['Close']].copy()
        else:
            st.error("No usable price data found for the selected ticker.")
            st.stop()
        raw_data.columns = [tickers[0]]

    raw_data.dropna(axis=1, how='all', inplace=True)
    available_tickers = raw_data.columns.tolist()

    if raw_data.empty or not available_tickers:
        st.error("No valid price data retrieved for selected tickers and dates.")
        st.stop()

    valid_weights = {ticker: weights[ticker] for ticker in available_tickers}
    returns = raw_data.pct_change().dropna()
    returns['Portfolio'] = sum(returns[ticker] * valid_weights[ticker] for ticker in valid_weights)

except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# Risk Metrics
def calculate_historical_var(series, confidence=0.95):
    sorted_returns = series.sort_values()
    index = int((1 - confidence) * len(sorted_returns))
    return -sorted_returns.iloc[index]

def calculate_expected_shortfall(series, confidence=0.95):
    threshold = np.percentile(series, (1 - confidence) * 100)
    return -series[series <= threshold].mean()

portfolio_returns = returns['Portfolio']
z_score = norm.ppf(confidence_level)
rolling_vol = portfolio_returns.rolling(vol_window).std().iloc[-1]

if var_method == "Full-window percentile":
    parametric_var = -np.percentile(portfolio_returns, (1 - confidence_level) * 100)
else:
    parametric_var = z_score * rolling_vol

historical_var = calculate_historical_var(portfolio_returns, confidence=confidence_level)
expected_shortfall = calculate_expected_shortfall(portfolio_returns, confidence=confidence_level)
annual_volatility = rolling_vol * np.sqrt(252)

# Export Report
def convert_df_to_csv(df):
    return df.to_csv(index=True).encode('utf-8')

report_df = pd.DataFrame({
    "Metric": [
        f"Parametric VaR ({int(confidence_level*100)}%)",
        f"Historical VaR ({int(confidence_level*100)}%)",
        f"Expected Shortfall ({int(confidence_level*100)}%)",
        "Annualized Volatility"
    ],
    "Value": [
        f"{parametric_var:.2%}",
        f"{historical_var:.2%}",
        f"{expected_shortfall:.2%}",
        f"{annual_volatility:.2%}"
    ]
})

csv = convert_df_to_csv(report_df)

# Dashboard Display
st.subheader("Portfolio Risk Summary")

col1, col2 = st.columns(2)
col1.metric(label=f"{int(confidence_level*100)}% Parametric VaR", value=f"{parametric_var:.2%}")
col2.metric(label=f"{int(confidence_level*100)}% Historical VaR", value=f"{historical_var:.2%}")
st.metric(label=f"{int(confidence_level*100)}% Expected Shortfall", value=f"{expected_shortfall:.2%}")
st.metric(label="Annualized Volatility", value=f"{annual_volatility:.2%}")

st.caption(
    "Note: Parametric VaR assumes returns are normally distributed. When using the rolling volatility method, the model reflects the most recent market behavior."
)

if parametric_var > 0.03 or historical_var > 0.03:
    st.warning("⚠️ One or more VaR metrics exceed 3% — consider reducing risk exposure.")

st.download_button("📥 Download Risk Summary (CSV)", data=csv, file_name="risk_report.csv", mime='text/csv')

st.subheader("Rolling Volatility")
st.line_chart(portfolio_returns.rolling(vol_window).std())

st.subheader("Return Distribution")
fig, ax = plt.subplots()
portfolio_returns.hist(bins=50, ax=ax, color='skyblue', edgecolor='black')
ax.axvline(-parametric_var, color='red', linestyle='--', label='Parametric VaR')
ax.axvline(-historical_var, color='green', linestyle='--', label='Historical VaR')
ax.axvline(-expected_shortfall, color='orange', linestyle='--', label='Expected Shortfall')
ax.set_title('Distribution of Daily Portfolio Returns')
ax.legend()
st.pyplot(fig)
