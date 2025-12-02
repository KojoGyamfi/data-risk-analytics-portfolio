# Monte Carlo Pricing Engine (GBM, European Options)

This is a small, readable Monte Carlo engine for pricing European options
under a risk–neutral Geometric Brownian Motion (GBM) model.

It includes:

- A `GBMModel` that simulates terminal prices under GBM.
- A `EuropeanOption` payoff.
- A `MonteCarloEngine` that:
  - simulates paths,
  - computes discounted payoffs,
  - returns the price, standard error, and a 95% confidence interval.
- A Black–Scholes closed–form implementation for sanity checks.
- A Streamlit app for visual exploration.

## Quick start

```bash
pip install -r requirements.txt
```

Sanity check from the project root:

```bash
python quick_test.py
```

Streamlit app:

```bash
streamlit run streamlit_app.py
```
