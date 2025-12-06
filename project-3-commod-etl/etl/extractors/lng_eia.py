from __future__ import annotations

from datetime import date, datetime
from typing import List
import logging

import pandas as pd
import requests

from .base import BaseExtractor
from etl.config import EIA_API_KEY

logger = logging.getLogger(__name__)


class LNGEIAExtractor(BaseExtractor):
    """Extractor for LNG / natural gas prices via the EIA Open Data API.

    For portfolio/demo use we fetch a single series, such as:
      - Henry Hub daily spot prices (series_id='NG.RNGWHHD.D')
      - or a monthly LNG export price series

    You can configure the EIA series ID via constructor.
    """

    name = "EIA_API"
    BASE_URL = "https://api.eia.gov/series/"

    def __init__(self, series_id: str = "NG.RNGWHHD.D") -> None:
        if EIA_API_KEY is None:
            raise RuntimeError(
                "EIA_API_KEY is not set. "
                "Set it in your environment or .env file to use LNGEIAExtractor."
            )
        self.series_id = series_id

    def fetch_prices(self, start_date: date, end_date: date) -> pd.DataFrame:
        params = {
            "api_key": EIA_API_KEY,
            "series_id": self.series_id,
        }

        logger.info(
            "Requesting EIA series %s from %s to %s",
            self.series_id,
            start_date,
            end_date,
        )

        resp = requests.get(self.BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        # EIA API returns data as list of [date_string, value] under
        # data['series'][0]['data']
        series = data["series"][0]
        rows = series["data"]

        records = []
        for date_str, value in rows:
            # Date formats vary by frequency; for simplicity we handle
            # daily ('YYYYMMDD') and monthly ('YYYYMM') here.
            if len(date_str) == 8:  # daily
                dt = datetime.strptime(date_str, "%Y%m%d").date()
            elif len(date_str) == 6:  # monthly
                dt = datetime.strptime(date_str, "%Y%m").date()
            else:
                # Skip unsupported frequencies for this demo
                continue

            if start_date <= dt <= end_date:
                records.append({"trade_date": dt, "price": float(value)})

        df = pd.DataFrame.from_records(records)
        if df.empty:
            logger.warning("No EIA data returned in requested window.")
        return df
