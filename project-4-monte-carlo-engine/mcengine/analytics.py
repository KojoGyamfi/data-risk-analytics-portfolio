from __future__ import annotations

import math

from .models import GBMModel
from .products import EuropeanOption, OptionType


def _norm_cdf(x: float) -> float:
    """Standard normal CDF using erf.
    This is good enough for pricing tests and avoids pulling in SciPy.
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_price(model: GBMModel, option: EuropeanOption) -> float:
    """Black–Scholes price for a European call or put.
    Assumes a non–dividend–paying asset following:
    dS_t = r S_t dt + sigma S_t dW_t
    under the risk–neutral measure.
    """
    S0 = model.spot
    K = option.strike
    T = option.maturity
    r = model.rate
    sigma = model.vol

    if T <= 0:
        if option.option_type == OptionType.CALL:
            return max(S0 - K, 0.0)
        return max(K - S0, 0.0)

    d1 = (math.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option.option_type == OptionType.CALL:
        price = S0 * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
    else:
        price = K * math.exp(-r * T) * _norm_cdf(-d2) - S0 * _norm_cdf(-d1)

    return float(price)
