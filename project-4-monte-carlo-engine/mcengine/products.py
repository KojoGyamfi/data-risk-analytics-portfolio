from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import numpy as np


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


@dataclass
class EuropeanOption:
    strike: float
    maturity: float  # T in years
    option_type: OptionType = OptionType.CALL

    def payoff(self, terminal_prices: np.ndarray) -> np.ndarray:
        """Vectorised payoff for a batch of terminal prices.

        Parameters
        ----------
        terminal_prices:
        Array of S_T values, shape (n_paths,).

        Returns
        -------
        np.ndarray
        Array of payoffs, shape (n_paths,).
        """
        if self.option_type == OptionType.CALL:
            return np.maximum(terminal_prices - self.strike, 0.0)
        return np.maximum(self.strike - terminal_prices, 0.0)
