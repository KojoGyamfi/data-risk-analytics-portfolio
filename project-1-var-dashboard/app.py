import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------
# Simulate data
# ------------------------------
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', periods=252)
returns = np.random.normal(loc=0.0005, scale=0.02, size=(252, 3))  # 3 assets
df = pd.DataFrame(returns, index=dates, columns=['Asset A', 'Asset B', 'Asset C'])
df['Portfolio'] = df.mean(axis=1)

# ------------------------------
# Functions
# ------------------------------
def calculate_var(series, confidence=0.95):
    return -np.percentile(series, (1 - confidence) * 100)

def rolling_volatility(series, window=20):
    return series.rolling(window).std()

# ------------------------------
# Streamlit UI
# ------------------------------
st.title("Daily VaR Dashboard – Multi-Asset Portfolio")

st.sidebar.header("Settings")
confidence_level = st.sidebar.slider("Confidence Level", 0.90, 0.99, 0.95)
window_size = st.sidebar.slider("Volatility Window (days)", 10, 60, 20)

st.subheader("Latest Portfolio VaR")
latest_var = calculate_var(df['Portfolio'], confidence=confidence_level)
st.metric(label=f"{int(confidence_level * 100)}% 1-Day VaR", value=f"{latest_var:.2%}")

# ------------------------------
# Plots
# ------------------------------
st.subheader("Rolling Volatility")
rolling_vol = rolling_volatility(df['Portfolio'], window=window_size)
st.line_chart(rolling_vol)

st.subheader("Portfolio Return Distribution")
fig, ax = plt.subplots()
df['Portfolio'].hist(bins=50, ax=ax)
ax.axvline(-latest_var, color='red', linestyle='--', label='VaR Threshold')
ax.set_title('Distribution of Daily Returns')
ax.legend()
st.pyplot(fig)
