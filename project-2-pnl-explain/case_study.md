#  Case Study: Multi-Day P&L Attribution Tool for a Global Options Book

---

##  Problem

Risk managers and product controllers often struggle to understand **why** a portfolio’s P&L has moved, especially in volatile conditions or when portfolios span multiple sectors, regions, and instrument types. Traditional reporting lacks the granularity or modeling transparency required to confidently explain daily P&L at scale — particularly for complex derivative books.

---

##  Solution

This project delivers a dynamic, interactive **P&L Attribution Dashboard** built using **Python and Streamlit**. The tool enables users to:

- Decompose **actual P&L** into **explained P&L** based on Greek sensitivities:
  - **Delta** × ΔSpot  
  - **Gamma** × ΔSpot²  
  - **Vega** × ΔVol  
  - **Theta** × ΔTime
- Visualize P&L evolution across:
  - 30 days of simulated portfolio data
  - Sectors, regions, tickers, and position direction (long/short)
- Drill down into:
  - Trade-level residuals
  - Daily attribution across all Greeks
- Track **cumulative trends** in actual vs explained P&L
- Flag **unexplained residuals** for further investigation

---

##  Technical Highlights

- **Tech Stack:** Python, Pandas, NumPy, Streamlit, Altair
- **Data Modeling:**
  - Synthetic options portfolio with sector/region diversity
  - Simulated market time series (spot and vol) with realistic noise
  - Position-level Greeks and actual P&L
- **Core Analytics:**
  - Taylor-series based explained P&L attribution
  - Residual calculation (actual − explained)
  - Cumulative P&L over time
- **Interactive Features:**
  - Group-by toggles (e.g. sector, region, long/short)
  - Greek attribution tables and charts
  - Trade-level drilldowns
  - Date range filtering

---

##  Impact & Use Cases

- Helps **quantify and explain daily P&L** across complex portfolios
- Ideal for:
  - Derivatives risk teams
  - Product controllers
  - Risk analytics consultants
- Useful for:
  - Highlighting modeling errors or trade booking issues
  - Residual anomaly detection
  - Improving sign-off workflows with transparent logic

---

##  How to Run

See the [README.md](./README.md) for setup instructions.

Or launch the dashboard locally using:

```bash
streamlit run dashboard.py
