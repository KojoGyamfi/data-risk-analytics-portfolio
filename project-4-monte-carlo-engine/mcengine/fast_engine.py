from __future__ import annotations

from dataclasses import dataclass

from .models import GBMModel
from .products import EuropeanOption, OptionType

try:
    # Compiled C++ extension built by `python setup.py build_ext --inplace`
    from . import _mc_core
except ImportError:
    _mc_core = None


@dataclass
class FastMCConfig:
    n_paths: int
    seed: int | None = None


def price_european_mc_cpp(
    model: GBMModel,
    option: EuropeanOption,
    config: FastMCConfig,
) -> dict:
    """
    Price a European option using the C++ Monte Carlo backend.

    Returns a dict in the same shape as the Python engine:
        {
          "price": float,
          "std_error": float,
          "conf_int_95": (lower, upper)
        }
    """
    if _mc_core is None:
        raise RuntimeError(
            "C++ backend (_mc_core) is not available. "
        )

    if config.seed is None:
        seed = 42  # simple default
    else:
        seed = int(config.seed)

    is_call = option.option_type == OptionType.CALL

    # Call into C++ via pybind11
    raw = _mc_core.mc_price_european(
        S0=float(model.spot),
        K=float(option.strike),
        r=float(model.rate),
        sigma=float(model.vol),
        T=float(option.maturity),
        n_paths=int(config.n_paths),
        seed=int(seed),
        is_call=bool(is_call),
    )

    price = float(raw["price"])
    std_error = float(raw["std_error"])

    # Use the same 95% CI convention as the Python engine
    z = 1.96
    ci_lower = price - z * std_error
    ci_upper = price + z * std_error

    return {
        "price": price,
        "std_error": std_error,
        "conf_int_95": (ci_lower, ci_upper),
    }
