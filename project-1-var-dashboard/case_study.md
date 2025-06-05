#  Case Study: Daily VaR & Risk Dashboard for a Multi-Asset Portfolio

---

##  Problem

Risk managers and analysts need accessible, transparent tools to evaluate portfolio risk in volatile market environments. Enterprise systems are often opaque or inflexible, making it difficult to simulate, explain, or customize risk metrics — especially for smaller firms or fast-moving asset classes like commodities and tech.

---

##  Solution

This project delivers a responsive, interactive Value-at-Risk (VaR) dashboard using **Python and Streamlit**. The tool enables users to:

- Calculate **Value at Risk (VaR)** using both:
  - **Historical VaR** (non-parametric percentile method)
  - **Parametric VaR** (z-score × rolling volatility)
- Customize:
  - Portfolio asset selection (up to 5 tickers)
  - Asset weights (with real-time validation)
  - Confidence level (95% or 99%)
  - Rolling volatility window size
- Visualize:
  - Daily return distribution with VaR overlays
  - Rolling portfolio volatility
- Export risk reports as CSV summaries for documentation or reporting

---

## 🛠 Technical Highlights

- **Tech stack:** Python, Streamlit, yFinance, Pandas, NumPy, Matplotlib
- **Core Metrics:**
  - Parametric VaR (normal distribution, rolling volatility)
  - Historical VaR (empirical distribution)
  - Expected Shortfall (CVaR)
  - Annualized Volatility
- **Interactive Features:**
  - Toggle between parametric VaR methods
  - Tooltip guidance for risk assumptions
  - Input validation for weights and dates
  - Visual risk warnings for high VaR

---

##  Impact & Use Cases

- Enables **fast, interpretable portfolio risk analysis** without enterprise tools
- Ideal for:
  - Boutique asset managers
  - Commodity and energy analysts
  - Data/risk consultants
- Easily extendable for:
  - Asset-level risk attribution
  - Limit monitoring
  - Multi-scenario stress testing

---

##  How to Run

See the [README.md](./README.md) for setup instructions.

Or launch the dashboard locally using:
```bash
streamlit run app.py
