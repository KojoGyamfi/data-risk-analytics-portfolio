"""Small sanity check script for the Monte Carlo engine.
Run with:
python quick_test.py
from the project root.
"""

from mcengine import (
    GBMModel,
    EuropeanOption,
    OptionType,
    MonteCarloConfig,
    MonteCarloEngine,
    black_scholes_price,
)

def main() -> None:
    model = GBMModel(spot=100.0, rate=0.02, vol=0.2)
    option = EuropeanOption(strike=100.0, maturity=1.0, option_type=OptionType.CALL)
    cfg = MonteCarloConfig(n_paths=200_000, seed=42)

    engine = MonteCarloEngine(model, cfg)
    mc_result = engine.price(option)
    bs_price = black_scholes_price(model, option)

    print("Monte Carlo result:")
    print(mc_result)
    print()
    print(f"Black–Scholes price: {bs_price:.6f}")

if __name__ == "__main__":
    main()
