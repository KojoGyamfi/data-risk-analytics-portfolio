# Project 1 – Daily VaR Dashboard for a Multi-Asset Portfolio

## 🧾 Overview
This project demonstrates a daily Value-at-Risk (VaR) dashboard for a multi-asset portfolio using Python and Streamlit. It simulates historical price data, calculates rolling VaR, and visualizes key portfolio risk metrics for decision support.

Designed to replicate the kind of daily risk summaries used by risk managers, portfolio analysts, and front office teams to assess potential losses and ensure risk limit compliance.

---

## 🛠 Features
- Simulates daily returns for a portfolio of assets
- Calculates 1-day historical and parametric VaR (95% and 99%)
- Rolling volatility and return distribution visualizations
- Streamlit dashboard with:
  - Portfolio VaR and volatility summary
  - Risk over time charts
  - Distribution plots
- Easily extendable to real market data (e.g. via Yahoo Finance API)

---

## 📁 Files Included
- `var_calculation.py`: Functions for VaR and volatility calculation
- `dashboard.ipynb`: Jupyter Notebook with data simulation and exploratory analysis
- `app.py`: Streamlit dashboard script
- `sample_data.csv`: Simulated daily returns (if applicable)
- `/assets/`: Screenshots of dashboard and plots

---

## 📊 Key Concepts Demonstrated
- Value-at-Risk (Historical & Parametric)
- Risk visualization for multi-asset portfolios
- Basic data simulation & preprocessing
- Python-based dashboarding for risk reporting

---

## 🔧 How to Run
1. Clone the repo or download the folder
2. Install required packages:
```bash
pip install pandas numpy matplotlib streamlit
streamlit run app.py
