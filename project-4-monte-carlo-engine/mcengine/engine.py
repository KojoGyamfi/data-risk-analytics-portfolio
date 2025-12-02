from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .models import GBMModel
from .products import EuropeanOption


@dataclass
class MonteCarloConfig:
    n_paths: int
    seed: int | None = None


class MonteCarloEngine:
    """Simple Monte Carlo engine for pricing European options under GBM."""

    def __init__(self, model: GBMModel, config: MonteCarloConfig) -> None:
        self.model = model
        self.cfg = config
        self.rng = np.random.default_rng(config.seed)

    def price(self, product: EuropeanOption) -> dict:
        """Price a European option with Monte Carlo.
        Returns a small dict instead of a custom class so it's easy to
        inspect and serialise:

        {
          "price": float,
          "std_error": float,
          "conf_int_95": (lower, upper)
        }
        """
        T = product.maturity

        # 1) Simulate terminal prices under the model
        terminal_prices = self.model.simulate_terminal(
            T=T,
            n_paths=self.cfg.n_paths,
            rng=self.rng,
        )

        # 2) Map prices -> payoffs
        payoffs = product.payoff(terminal_prices)

        # 3) Discount each payoff back to today
        disc_factor = np.exp(-self.model.rate * T)
        discounted = disc_factor * payoffs  # X_i in the maths

        # 4) Monte Carlo estimator (sample mean)
        price_estimate = float(discounted.mean())

        # 5) Estimated standard error via sample variance
        sample_std = float(discounted.std(ddof=1))
        std_error = sample_std / np.sqrt(self.cfg.n_paths)

        # 6) 95% confidence interval from CLT
        z = 1.96
        ci_lower = price_estimate - z * std_error
        ci_upper = price_estimate + z * std_error

        return {
            "price": price_estimate,
            "std_error": float(std_error),
            "conf_int_95": (float(ci_lower), float(ci_upper)),
        }
