#  P&L Explain Tool – Equity Derivatives Edition

This tool is designed to perform P&L attribution for an equity derivatives trading book using Greek-based sensitivity analysis. It enables users to decompose daily P&L into key explanatory factors such as Delta, Gamma, Vega, and Theta, and compare these to actual realized P&L for validation and analysis.

---

##  Project Overview

**Goal:**  
Help traders and risk managers understand what drove their daily P&L and identify unexplained components.

**Scope:**  
- Derivatives positions (calls, puts, delta-one)
- Greek sensitivities (Delta, Gamma, Vega, Theta)
- Market data (spot and implied vol)
- Actual realized P&L
- Explained vs. unexplained breakdown

---

##  Project Structure

- `data/`
  - `market_data.csv` — Spot and vol data for 5 underlyings across 2 days
  - `positions.csv` — Position-level exposures with Greek sensitivities
  - `pnl_actuals.csv` — Realized daily P&L per trade

- `pnl_explain.py` — Core attribution logic using first- and second-order Greeks

- `dashboard.py` (optional) — Interactive Streamlit dashboard (to be developed)

- `README.md` — Project documentation

- `requirements.txt` — Dependencies

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

