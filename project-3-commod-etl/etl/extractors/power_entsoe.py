from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List
import logging

import pandas as pd
import requests

from .base import BaseExtractor
from etl.config import ENTSOE_API_TOKEN

logger = logging.getLogger(__name__)


class PowerEntsoeExtractor(BaseExtractor):
    """Extractor for European power day-ahead prices via ENTSO-E API.

    This implementation is intentionally minimal and designed for portfolio
    purposes. It assumes:
    - you have an ENTSOE_API_TOKEN set in your environment/.env
    - you are interested in one bidding zone (e.g. 'DE-LU', 'GB')

    The ENTSO-E API returns XML; here we hit the REST endpoint and parse
    it into a DataFrame with columns:
        trade_date, contract, price
    """

    name = "ENTSOE_API"

    BASE_URL = "https://web-api.transparency.entsoe.eu/api"

    def __init__(self, bidding_zone: str) -> None:
        if ENTSOE_API_TOKEN is None:
            raise RuntimeError(
                "ENTSOE_API_TOKEN is not set. "
                "Set it in your environment or .env file to use PowerEntsoeExtractor."
            )
        self.bidding_zone = bidding_zone

    def _build_params(self, start_date: date, end_date: date) -> dict:
        # ENTSO-E expects datetime strings in YYYYMMDDHHMM format, CET/CEST.
        # For a daily ETL we can request a from/to window spanning the days.
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())

        return {
            "securityToken": ENTSOE_API_TOKEN,
            "documentType": "A44",        # Day-ahead prices
            "in_Domain": self.bidding_zone,
            "out_Domain": self.bidding_zone,
            "periodStart": start_dt.strftime("%Y%m%d%H%M"),
            "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
        }

    def fetch_prices(self, start_date: date, end_date: date) -> pd.DataFrame:
        params = self._build_params(start_date, end_date)

        logger.info(
            "Requesting ENTSO-E day-ahead prices for %s from %s to %s",
            self.bidding_zone,
            start_date,
            end_date,
        )

        resp = requests.get(f"{self.BASE_URL}/dayaheadtotalaggregated", params=params)
        resp.raise_for_status()

        # For simplicity and because XML formats can change, we'll keep this
        # as a placeholder parser that expects a preprocessed JSON-like structure.
        # In a real implementation you'd parse resp.text (XML) with lxml or
        # xml.etree and extract the hourly prices, then aggregate to daily.
        #
        # Here we just raise a clear error so it's obvious where to plug in.
        raise NotImplementedError(
            "PowerEntsoeExtractor.fetch_prices currently does not parse the XML "
            "response. Implement XML parsing here to return a DataFrame with "
            "columns ['trade_date', 'contract', 'price']."
        )
