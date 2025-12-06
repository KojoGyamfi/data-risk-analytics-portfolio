# Data & Risk Analytics Portfolio

Welcome to my portfolio showcasing tools and analytics projects focused on financial markets, risk management, and data infrastructure.

Each project is built around a practical use case, with an emphasis on clean engineering, reproducible analytics, and clear visualisation.

---

## Projects

1. **[VaR Dashboard for Multi-Asset Portfolios](./project-1-var-dashboard)**  
   Risk dashboard for multi-asset portfolios, visualising Value-at-Risk (VaR), rolling volatility, and exposure breakdowns.  
   Built with Python and Streamlit to explore portfolio risk under different scenarios and horizons.

2. **[P&L Explain Tool with Greek Attribution](./project-2-pnl-explain)**  
   P&L decomposition tool for options portfolios, breaking daily P&L into key drivers such as delta, gamma, vega, theta, and residuals.  
   Designed to mimic production-style risk/P&L explain workflows with a structured ETL layer and analytics/reporting layer.

3. **[Commodities Price ETL & Power/Gas Dashboard](./project-3-commodities-etl)**  
   End-to-end ETL pipeline for commodities market data, pulling:  
   - European power day-ahead prices from **ENTSO-E**, and  
   - Henry Hub natural gas spot prices from the **EIA Open Data API (v2)**.  

   Data is normalised into a single `prices` table (SQLite by default, easily switchable to Postgres), and exposed via a Streamlit app.

4. **[Monte Carlo Pricing Engine for European Options](./project-4-monte-carlo-engine)**  
   Monte Carlo engine to price European options under Geometric Brownian Motion (GBM), with:
   - a **C++** core for path generation and payoff computation,
   - **pybind11** bindings into Python, and
   - a **Streamlit** front-end to visualise price convergence, GBM paths, and payoff distributions.  

   The project emphasises both the mathematical side (risk-neutral pricing, Monte Carlo estimators) and the engineering side (C++/Python integration, performance vs readability).

---

Each folder includes code, documentation, and sample outputs where relevant.  
Feel free to explore the projects or reach out with questions or ideas for extensions.
