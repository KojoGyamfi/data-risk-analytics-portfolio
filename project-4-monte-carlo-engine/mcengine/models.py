from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class GBMModel:
    """Risk–neutral Geometric Brownian Motion model.

    dS_t = r S_t dt + sigma S_t dW_t
    """

    spot: float   # S0
    rate: float   # r
    vol: float    # sigma

    def simulate_terminal(
        self,
        T: float,
        n_paths: int,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Simulate terminal prices S_T under GBM.

        Parameters
        ----------
        T: Time to maturity in years.
        n_paths: Number of Monte Carlo paths.
        rng: NumPy random generator (for reproducibility).

        Returns
        -------
        np.ndarray
        Array of shape (n_paths,) with simulated terminal prices S_T.
        """
        Z = rng.standard_normal(n_paths)
        drift = (self.rate - 0.5 * self.vol**2) * T
        diffusion = self.vol * np.sqrt(T) * Z
        return self.spot * np.exp(drift + diffusion)
