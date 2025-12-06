from __future__ import annotations

from datetime import date, timedelta
import logging

import pandas as pd
from entsoe import EntsoePandasClient

from .base import BaseExtractor
from etl.config import ENTSOE_API_TOKEN

logger = logging.getLogger(__name__)


class PowerEntsoeExtractor(BaseExtractor):
    """Extractor for European power day-ahead prices via ENTSO-E API.

    Uses the `entsoe-py` client under the hood.

    - Queries day-ahead prices for a given bidding zone (e.g. "DE-LU", "GB")
    - Aggregates hourly prices to a daily average per trade_date
    """

    name = "ENTSOE_API"

    def __init__(self, bidding_zone: str, tz: str = "Europe/Brussels") -> None:
        if not ENTSOE_API_TOKEN:
            raise RuntimeError(
                "ENTSOE_API_TOKEN is not set. "
                "Set it in your environment or .env file to use PowerEntsoeExtractor."
            )
        self.client = EntsoePandasClient(api_key=ENTSOE_API_TOKEN)
        self.bidding_zone = bidding_zone
        self.tz = tz

    def fetch_prices(self, start_date: date, end_date: date) -> pd.DataFrame:
        # entsoe-py expects timezone-aware pandas Timestamps
        start_ts = pd.Timestamp(start_date).tz_localize(self.tz)
        # end is exclusive, so go one day beyond end_date
        end_ts = pd.Timestamp(end_date + timedelta(days=1)).tz_localize(self.tz)

        logger.info(
            "Requesting ENTSO-E day-ahead prices for %s from %s to %s",
            self.bidding_zone,
            start_date,
            end_date,
        )
        series = self.client.query_day_ahead_prices(
            self.bidding_zone,
            start=start_ts,
            end=end_ts,
        )
        # Series indexed by hourly datetime; compute daily average price
        df = series.to_frame(name="price").reset_index(drop=False)
        df.rename(columns={"index": "datetime"}, inplace=True)
        df["trade_date"] = df["datetime"].dt.date
        daily = df.groupby("trade_date", as_index=False)["price"].mean()
        daily["contract"] = "Day-Ahead Baseload"

        return daily[["trade_date", "contract", "price"]]
