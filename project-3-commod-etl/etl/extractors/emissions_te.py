from __future__ import annotations

from datetime import date, datetime
import logging

import pandas as pd
import requests

from .base import BaseExtractor
from etl.config import TE_CLIENT, TE_SECRET

logger = logging.getLogger(__name__)


class EmissionsTradingEconomicsExtractor(BaseExtractor):
    """Extractor for EU carbon permits via TradingEconomics API.

    This uses the 'EU Carbon Permits' commodity (symbol 'EECXM:IND').

    Docs: https://docs.tradingeconomics.com/ (requires free API account)
    """

    name = "TE_API"
    BASE_URL = "https://api.tradingeconomics.com/markets/historical"

    def __init__(self, symbol: str = "EECXM:IND") -> None:
        if not (TE_CLIENT and TE_SECRET):
            raise RuntimeError(
                "TE_CLIENT and TE_SECRET are not set. "
                "Set them in your environment or .env file to use "
                "EmissionsTradingEconomicsExtractor."
            )
        self.symbol = symbol

    def fetch_prices(self, start_date: date, end_date: date) -> pd.DataFrame:
        params = {
            "symbol": self.symbol,
            "client": TE_CLIENT,
            "secret": TE_SECRET,
            "format": "json",
        }

        logger.info(
            "Requesting TradingEconomics emissions data for %s from %s to %s",
            self.symbol,
            start_date,
            end_date,
        )

        resp = requests.get(self.BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        records = []
        for item in data:
            # Example fields: 'Date', 'Close', 'Unit'
            dt = datetime.fromisoformat(item["Date"]).date()
            if start_date <= dt <= end_date:
                price = float(item["Close"])
                records.append(
                    {
                        "trade_date": dt,
                        "price": price,
                        "unit": item.get("Unit", "EUR"),
                    }
                )

        df = pd.DataFrame.from_records(records)
        if df.empty:
            logger.warning("No TradingEconomics data returned in requested window.")
        return df
