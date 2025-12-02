import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

from mcengine import (
    GBMModel,
    EuropeanOption,
    OptionType,
    MonteCarloConfig,
    MonteCarloEngine,
    FastMCConfig,
    price_european_mc_cpp,
    black_scholes_price,
)


st.set_page_config(page_title="Monte Carlo Option Pricer", layout="wide")

st.title("Monte Carlo Pricing Engine — European Option under GBM")

st.markdown(
    """
This app prices a European option by Monte Carlo under a
risk–neutral Geometric Brownian Motion (GBM) model and compares the result
to the Black–Scholes closed–form price (for calls).

You can switch between a **pure Python/NumPy backend** and a
**C++ backend exposed via pybind11**, and visualise:

- The distribution of discounted payoffs,
- The distribution of terminal prices \\(S_T\\),
- Sample GBM paths coloured by whether they expire ITM/ATM or OTM.
"""
)


# Sidebar controls

st.sidebar.header("Model parameters")
S0 = st.sidebar.number_input("Spot price S₀", value=100.0, step=1.0)
r = st.sidebar.number_input("Risk–free rate r", value=0.02, step=0.005, format="%.3f")
sigma = st.sidebar.number_input("Volatility σ", value=0.2, step=0.01, format="%.3f")

st.sidebar.header("Option parameters")
K = st.sidebar.number_input("Strike K", value=100.0, step=1.0)
T = st.sidebar.number_input("Maturity T (years)", value=1.0, step=0.25, format="%.2f")
opt_type_str = st.sidebar.selectbox("Option type", ["Call", "Put"])
opt_type = OptionType.CALL if opt_type_str == "Call" else OptionType.PUT

st.sidebar.header("Monte Carlo parameters")
n_paths = st.sidebar.number_input("Number of paths", value=100_000, step=10_000)
seed = st.sidebar.number_input("Random seed", value=42, step=1)

st.sidebar.header("Backend")
backend = st.sidebar.selectbox(
    "Monte Carlo backend",
    ["Python (NumPy)", "C++ (pybind11)"],
)

st.sidebar.header("Path visualisation")
n_plot_paths = st.sidebar.number_input(
    "Number of GBM paths to plot",
    value=20,
    min_value=1,
    max_value=500,
)
n_time_steps = st.sidebar.number_input(
    "Time steps for GBM paths",
    value=100,
    min_value=5,
    max_value=1000,
)

run_button = st.sidebar.button("Run simulation")

# Main logic

if run_button:
    # Shared model & option objects
    model = GBMModel(spot=S0, rate=r, vol=sigma)
    option = EuropeanOption(strike=K, maturity=T, option_type=opt_type)

    # Price using selected backend
    if backend.startswith("Python"):
        cfg = MonteCarloConfig(n_paths=int(n_paths), seed=int(seed))
        engine = MonteCarloEngine(model, cfg)

        with st.spinner("Running Python/NumPy Monte Carlo simulation..."):
            result = engine.price(option)
    else:
        fast_cfg = FastMCConfig(n_paths=int(n_paths), seed=int(seed))
        try:
            with st.spinner("Running C++ Monte Carlo simulation via pybind11..."):
                result = price_european_mc_cpp(model, option, fast_cfg)
        except RuntimeError as exc:
            st.error(
                "C++ backend is not available. "
                "Make sure you built the extension with "
                "`python setup.py build_ext --inplace`.\n\n"
                f"Details: {exc}"
            )
            st.stop()

    # Closed-form Black–Scholes (only for calls, non-dividend-paying)
    bs_price = (
        black_scholes_price(model, option)
        if opt_type == OptionType.CALL
        else None
    )

    # Pricing results
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pricing results")
        st.write(f"**Backend:** {backend}")
        st.write(f"**Monte Carlo price:** {result['price']:.4f}")
        st.write(f"**Std. error:** {result['std_error']:.6f}")
        ci_low, ci_high = result["conf_int_95"]
        st.write(
            f"**95% confidence interval:** "
            f"[{ci_low:.4f}, {ci_high:.4f}]"
        )

        if bs_price is not None:
            st.write(f"**Black–Scholes price (call):** {bs_price:.4f}")

    # Resimulate for visualisation (using Python GBM for clarity)
    rng = np.random.default_rng(int(seed))
    ST = model.simulate_terminal(T=T, n_paths=int(n_paths), rng=rng)
    payoffs = option.payoff(ST)
    disc_factor = np.exp(-r * T)
    discounted = disc_factor * payoffs

    # Discounted payoff distribution
    with col2:
        st.subheader("Discounted payoff samples")

        df_discounted = pd.DataFrame({"Discounted payoff": discounted})
        st.bar_chart(df_discounted)
        st.caption(
            "Each bar corresponds to one Monte Carlo path. "
            "**x-axis:** path index. "
            "**y-axis:** discounted payoff (same currency as S₀)."
        )

        #  Histogram of terminal prices ST
    st.subheader("Distribution of terminal prices $S_T$")

    counts, bin_edges = np.histogram(ST, bins=100)
    bin_centres = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    df_hist = pd.DataFrame(
        {
            "bin_centre": bin_centres,
            "frequency": counts,
        }
    )

    hist_chart = (
        alt.Chart(df_hist)
        .mark_bar()
        .encode(
            x=alt.X(
                "bin_centre:Q",
                title="Terminal price S_T",
                axis=alt.Axis(format=".2f"), 
            ),
            y=alt.Y(
                "frequency:Q",
                title="Frequency (number of paths)",
            ),
        )
        .properties(height=300)
    )

    st.altair_chart(hist_chart, use_container_width=True)
    st.caption(
        "**x-axis:** terminal price bin centre "
        "**y-axis:** number of paths ending in that bin."
    )


    # Sample GBM paths over time, coloured by ITM/ATM vs OTM at expiry
    st.subheader("Sample GBM paths under risk–neutral dynamics")

    if T > 0:
        n_steps = int(n_time_steps)
        dt = T / n_steps
        time_grid = np.linspace(0.0, T, n_steps + 1)

        n_paths_plot = int(n_plot_paths)

        # paths: shape (n_paths_plot, n_steps + 1)
        paths = np.zeros((n_paths_plot, n_steps + 1))
        paths[:, 0] = S0

        rng_paths = np.random.default_rng(int(seed) + 1)

        for t_idx in range(1, n_steps + 1):
            Z = rng_paths.standard_normal(n_paths_plot)
            drift_dt = (r - 0.5 * sigma**2) * dt
            diff_dt = sigma * np.sqrt(dt) * Z
            paths[:, t_idx] = paths[:, t_idx - 1] * np.exp(drift_dt + diff_dt)

        # Determine ITM/ATM vs OTM status at maturity
        ST_paths = paths[:, -1]

        if opt_type == OptionType.CALL:
            # Call: ITM if S_T >= K, OTM otherwise
            itm_mask = ST_paths >= K
        else:
            # Put: ITM if S_T <= K, OTM otherwise
            itm_mask = ST_paths <= K

        status_labels = np.where(itm_mask, "ITM/ATM", "OTM")

        # Build a long-form DataFrame for Altair: one row per (time, path)
        records = []
        for i in range(n_paths_plot):
            status_i = status_labels[i]
            path_name = f"Path {i + 1}"
            for t_val, s_val in zip(time_grid, paths[i, :]):
                records.append(
                    {
                        "time": t_val,
                        "price": s_val,
                        "path": path_name,
                        "status": status_i,
                    }
                )

        df_paths_long = pd.DataFrame.from_records(records)

        # Altair line chart: colour by status (ITM/ATM vs OTM)
        chart = (
            alt.Chart(df_paths_long)
            .mark_line(opacity=0.8)
            .encode(
                x=alt.X(
                    "time:Q",
                    title="Time (years)",
                ),
                y=alt.Y(
                    "price:Q",
                    title="Price S_t (same currency as S₀)",
                ),
                color=alt.Color(
                    "status:N",
                    title="Moneyness at T",
                    scale=alt.Scale(
                        domain=["ITM/ATM", "OTM"],
                        range=["#2ECC71", "#FF4B4B"],  
                    ),
                ),
                detail="path:N",
            )
            .properties(height=400)
        )

        st.altair_chart(chart, use_container_width=True)
        st.caption(
            "**Lines:** individual simulated GBM paths. "
            "Paths coloured **green** finish ITM or ATM at maturity; "
            "paths coloured **red** finish OTM."
        )
    else:
        st.info("Maturity T must be > 0 to display GBM paths.")
