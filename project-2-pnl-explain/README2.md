# P&L Attribution Tool

This tool provides multi-day explained vs actual P&L attribution for a portfolio of options across multiple sectors and regions. It decomposes P&L into Greeks (Delta, Gamma, Vega, Theta), supports trade-level drilldowns, and visualizes attribution trends over time.

---

## Features

-  Group-by views: Sector, Region, Ticker, Long/Short
-  Multi-day attribution across 30 trading days
-  Cumulative P&L trends (Actual vs Explained)
-  Daily Greek breakdown (tabular + stacked area chart)
-  Trade-level drilldown by group
-  Residual analysis: Actual - Explained P&L

---

## File Structure



- `data/`
  - `explained_pnl_timeseries.csv` 
  - `market_data.csv` 
  - `positions.csv` 
  - `pnl_actuals.csv` 

- `pnl_model.py` 

- `dashboard.py` 

- `generate_synthetic_data.py` 

- `case_study.md` 
---

##  Attribution Methodology

This tool uses a **Taylor expansion** approximation to explain P&L:

\[
\text{Explained P\&L} = \Delta \cdot \Delta S + \frac{1}{2} \Gamma \cdot (\Delta S)^2 + \text{Vega} \cdot \Delta \sigma + \Theta \cdot \Delta t
\]

Where:
- ΔS = Spot change
- Δσ = Implied vol change
- Δt = Time (in days)

**Residual P&L** = Actual – Explained

---

##  Example Output

| Trade ID | Actual P&L | Delta P&L | Gamma P&L | Vega P&L | Theta P&L | Residual |
|----------|------------|-----------|-----------|----------|-----------|----------|
| T1       | £210.42    | £180.23   | £12.51    | £15.33   | £-5.00    | £7.35    |

---

##  Future Enhancements

- Streamlit dashboard for visual exploration
- Aggregation by ticker or portfolio
- Include Vomma/Vanna (higher-order Greeks)
- Residual heatmap or alerting system

---

##  How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt

