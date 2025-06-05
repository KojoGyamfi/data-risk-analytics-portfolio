# Project 1 – Daily VaR Dashboard with Real Portfolio Data

## 📌 Overview
This project delivers a real-data Value-at-Risk (VaR) dashboard using live market data, with interactive tools for defining and analyzing portfolio risk. Built with Python and Streamlit, it is suitable for use by risk managers, portfolio analysts, or trading teams seeking real-time VaR, volatility, and tail risk metrics.

---

## 🔧 Features
- Real-time price and return data via Yahoo Finance (`yfinance`)
- Customizable portfolio asset selection and weights
- Parametric 1-day VaR at 95% or 99% confidence level
- Expected Shortfall (Conditional VaR) for tail risk
- Rolling volatility with adjustable window
- Risk alerts for VaR threshold breaches
- Downloadable risk summary report in CSV format
- Visualizations for volatility trend and return distribution

---

## 📁 Files Included
- `app.py`: Main Streamlit dashboard
- `requirements.txt`: Python dependencies
- `/assets/`: Optional screenshots (not included by default)

---

## 🧠 Key Concepts Demonstrated
- Portfolio return modeling with real asset prices
- VaR and Expected Shortfall computation
- Rolling standard deviation for volatility monitoring
- Streamlit UI/UX for finance dashboards
- Financial risk reporting and alerting

---

## ▶️ How to Run the App
1. Clone this repo or download the folder
2. Install required packages:
   ```bash
   pip install streamlit pandas numpy yfinance matplotlib
