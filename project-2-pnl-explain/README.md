# 📊 P&L Attribution Tool

This tool provides multi-day explained vs actual P&L attribution for a portfolio of options across multiple sectors and regions. It decomposes P&L into Greeks (Delta, Gamma, Vega, Theta), supports trade-level drilldowns, and visualizes attribution trends over time.

---

## 🔧 Features

- 🗂️ Group-by views: Sector, Region, Ticker, Long/Short
- 🕒 Multi-day attribution across 30 trading days
- 📈 Cumulative P&L trends (Actual vs Explained)
- 📉 Daily Greek breakdown (tabular + stacked area chart)
- 🔍 Trade-level drilldown by group
- 🧮 Residual analysis: Actual - Explained P&L

---

## 📁 File Structure

```
project/
├── data/
│   ├── explained_pnl_timeseries.csv
│   ├── positions.csv
│   ├── market_data.csv
│   └── pnl_actuals.csv
├── generate_synthetic_data.py
├── pnl_model.py
└── dashboard.py
```

---

## ▶️ Usage

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Generate synthetic data
python generate_synthetic_data.py

# Step 3: Run the dashboard
streamlit run dashboard.py
```

---

## 🧪 Methodology

The explained P&L is computed using a Taylor expansion-based approximation:

- **Delta** × ΔSpot
- **½ Gamma** × ΔSpot²
- **Vega** × ΔVol
- **Theta** × 1 (daily time decay)

Then:

```
Residual = Actual P&L − Explained P&L
```

---

## 📈 Dashboard Preview

- **Summary Tables**: Actual vs Explained P&L by group
- **Greek Attribution**: Table + stacked area chart
- **Cumulative View**: Trends of explained vs actual P&L
- **Drilldown**: Inspect trades by ticker, sector, or region

---

## ✅ TODO / Future Features

- Residual heatmaps
- Alerts on unexplained residual spikes
- Filters for maturity and option type
- Download/export filtered data
- Residual decomposition by driver (vol skew, cross gamma, etc.)
