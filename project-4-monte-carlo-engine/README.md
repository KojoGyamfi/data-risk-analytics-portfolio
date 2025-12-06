# Project 4 – Monte Carlo GBM Option Pricing Engine (Python + C++)

This project implements a **Monte Carlo pricing engine** for European options under a **risk-neutral Geometric Brownian Motion (GBM)** model, with:

- A **pure Python/NumPy implementation** (for clarity and teaching),
- A **C++ backend exposed via pybind11** (for performance and “systems” signal),
- An interactive **Streamlit app** to explore distributions and GBM paths visually.

---

## 1. Problem & Motivation

We want to price a European option (call/put) written on an underlying asset $S_t$.

Under the usual assumptions (frictionless markets, no arbitrage, constant $r$ and $\sigma$), the **risk-neutral dynamics** of the underlying are:

$$
dS_t = r S_t\,dt + \sigma S_t\,dW_t,
$$

which has the solution:

$$
S_T = S_0 \exp\left[\left(r - \tfrac{1}{2}\sigma^2\right)T + \sigma \sqrt{T}\,Z\right], \quad Z \sim \mathcal{N}(0, 1).
$$

For a European option with payoff $\Phi(S_T)$, the **arbitrage-free price** at time 0 is:

$$
V_0 = e^{-rT} \mathbb{E}^{\mathbb{Q}}[\Phi(S_T)].
$$

Analytically, a European call has the **Black–Scholes formula**, but:

- Many real products are not analytically tractable,
- Monte Carlo is a general-purpose **numerical** method that extends to more complex payoffs.

This project therefore:

- Uses Monte Carlo under the risk-neutral measure to estimate $V_0$,
- Compares results against **Black–Scholes** for validation,
- Demonstrates how to go from **math → Python prototype → optimised C++ backend**.

---

## 2. Mathematical Approach

### 2.1 Risk-Neutral Simulation

Under the risk-neutral measure $\mathbb{Q}$, for maturity $T$:

$$
S_T = S_0 \exp\left[\left(r - \tfrac{1}{2}\sigma^2\right)T + \sigma \sqrt{T}\,Z\right],
\quad Z \sim \mathcal{N}(0, 1).
$$

We simulate $N$ independent paths $S_T^{(i)}$ and compute discounted payoffs:

- Call payoff: $\Phi(S_T) = \max(S_T - K, 0)$  
- Put payoff:  $\Phi(S_T) = \max(K - S_T, 0)$

Estimator:

$$
\hat{V}_0 = e^{-rT} \cdot \frac{1}{N}\sum_{i=1}^N \Phi\left(S_T^{(i)}\right).
$$

By the **Law of Large Numbers**, $\hat{V}_0 \to V_0$ as $N \to \infty$.

By the **Central Limit Theorem**, we also estimate a **standard error**:

$$
\text{StdErr}(\hat{V}_0) \approx \frac{\hat{\sigma}_{\text{payoff}}}{\sqrt{N}},
$$

and construct a 95% confidence interval.

### 2.2 Validation Against Black–Scholes

For calls, we also compute the **Black–Scholes price** and check that:

$$
\hat{V}_0^{\text{MC}} \approx V_0^{\text{BS}}
$$

within the Monte Carlo confidence interval. This validates:

- Correct risk-neutral dynamics,
- Correct discounting,
- Correct implementation.

---

## 3. Implementation Overview

### 3.1 Python Components (`mcengine` package)

- `models.py`  
  Defines `GBMModel` with parameters:
  - `spot` ($S_0$)
  - `rate` ($r$)
  - `vol`  ($\sigma$)  
  Provides:
  - `simulate_terminal(T, n_paths, rng)` → samples of $S_T$.

- `products.py`  
  Defines a `EuropeanOption` and an `OptionType` enum (CALL / PUT), with:
  - `strike` ($K$)
  - `maturity` ($T$)
  - `payoff(S_T)` → vectorised payoff.

- `engine.py`  
  `MonteCarloEngine` (pure Python/NumPy):
  - Takes a `GBMModel`, a `MonteCarloConfig` (`n_paths`, `seed`),
  - Simulates $S_T$,
  - Computes discounted payoffs,
  - Returns:
    ```python
    {
        "price": float,
        "std_error": float,
        "conf_int_95": (lower, upper),
    }
    ```

- `analytics.py`  
  Implements the analytic **Black–Scholes** price for calls (non-dividend-paying).

- `fast_engine.py`  
  `price_european_mc_cpp(model, option, config)`:
  - Thin wrapper around the **C++ backend** (see below),
  - Mirrors the Python engine output format.

### 3.2 C++ Backend (`cpp/` + pybind11)

- `mc_core.hpp` / `mc_core.cpp`  
  Implements a fast C++ Monte Carlo pricer:

  ```cpp
  struct MCResult { double price; double std_error; };

  MCResult mc_price_european(
      double S0,
      double K,
      double r,
      double sigma,
      double T,
      std::size_t n_paths,
      unsigned int seed,
      bool is_call
  );
