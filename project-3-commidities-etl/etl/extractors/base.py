from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

import pandas as pd


class BaseExtractor(ABC):
    """Abstract base class for commodity price extractors.

    Subclasses implement `fetch_prices` to return source-specific data that
    will be normalised by the transform layer.
    """

    name: str  # human-readable source name

    @abstractmethod
    def fetch_prices(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Fetch raw price data for the given date range.

        The returned DataFrame can be in a source-specific format but must
        at minimum contain:

        - 'trade_date' (datetime or date)
        - 'price'
        - optional 'contract'

        The transform layer will normalise columns and fill defaults.
        """
        raise NotImplementedError
