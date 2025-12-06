from __future__ import annotations

from datetime import date, datetime
import logging
from typing import Any, Dict, List

import pandas as pd
import requests

from .base import BaseExtractor
from etl.config import EIA_API_KEY

logger = logging.getLogger(__name__)


class GasEIAExtractor(BaseExtractor):
    """
    Extractor for natural gas prices via the EIA API v2.

    We use the Henry Hub spot *daily* series (NG.RNGWHHD.D) and call the
    v2 /seriesid endpoint, which automatically translates legacy v1 series
    IDs and returns data in the v2 JSON format.

      - Endpoint: https://api.eia.gov/v2/seriesid/{series_id}
      - Field 'period' holds the date (YYYY-MM-DD / YYYYMMDD / YYYY-MM).
      - Field 'value' (for price datasets) holds the numeric price.

    We then:
      - Parse the dates into Python date objects.
      - Filter to [start_date, end_date].
      - Return a tidy DataFrame with trade_date, contract, price.
    """

    name = "EIA_API"
    BASE_URL = "https://api.eia.gov/v2/seriesid/"

    # Daily Henry Hub natural gas spot price (legacy v1 series ID)
    DEFAULT_SERIES_ID = "NG.RNGWHHD.D"

    def __init__(self, series_id: str | None = None) -> None:
        if not EIA_API_KEY:
            raise RuntimeError(
                "EIA_API_KEY is not set. "
                "Set it in your environment or .env file to use GasEIAExtractor."
            )
        self.series_id = series_id or self.DEFAULT_SERIES_ID

    def _parse_period_to_date(self, period: Any) -> date | None:
        """
        Convert EIA 'period' field into a Python date.

        Handles formats like:
          - 'YYYY-MM-DD'
          - 'YYYY-MM'
          - 'YYYYMMDD'
          - 'YYYYMM'
          - 4-digit year (fallback)
        """
        if period is None:
            return None

        s = str(period)

        try:
            if "-" in s:
                # Could be YYYY-MM or YYYY-MM-DD
                if len(s) == 10:  # 2025-12-06
                    return datetime.strptime(s, "%Y-%m-%d").date()
                if len(s) == 7:  # 2025-12 -> treat as first of month
                    return datetime.strptime(s, "%Y-%m").date()
                return None
            # No dashes
            if len(s) == 8:  # 20251206
                return datetime.strptime(s, "%Y%m%d").date()
            if len(s) == 6:  # 202512
                return datetime.strptime(s, "%Y%m").date()
            if len(s) == 4:  # 2025
                return datetime.strptime(s, "%Y").date()
        except ValueError:
            return None

        return None

    def _extract_price_value(self, row: Dict[str, Any]) -> float | None:
        """
        Extract the numeric price from a v2 row.

        For price datasets this is usually in 'value'. As a fallback,
        we scan for the first numeric-looking field that isn't 'period'
        or a '*-units' metadata field.
        """
        if "value" in row:
            try:
                return float(row["value"])
            except (TypeError, ValueError):
                pass

        for key, v in row.items():
            if key == "period" or key.endswith("-units"):
                continue
            try:
                return float(v)
            except (TypeError, ValueError):
                continue

        return None

    def fetch_prices(self, start_date: date, end_date: date) -> pd.DataFrame:
        url = f"{self.BASE_URL}{self.series_id}"
        params = {"api_key": EIA_API_KEY}

        logger.info(
            "Requesting EIA v2 series %s from %s to %s",
            self.series_id,
            start_date,
            end_date,
        )

        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code != 200:
            logger.error(
                "EIA v2 request failed with status %s. Response: %s",
                resp.status_code,
                resp.text[:500],
            )
            return pd.DataFrame(columns=["trade_date", "contract", "price"])

        data = resp.json()

        try:
            response = data["response"]
            rows: List[Dict[str, Any]] = response["data"]
            date_format = response.get("dateFormat")
            frequency = response.get("frequency")
            logger.info(
                "EIA v2 series %s: frequency=%s, dateFormat=%s, rows=%s",
                self.series_id,
                frequency,
                date_format,
                len(rows),
            )
        except (KeyError, TypeError) as exc:
            logger.error("Unexpected EIA v2 response format: %s", exc)
            return pd.DataFrame(columns=["trade_date", "contract", "price"])

        records: List[Dict[str, Any]] = []

        for row in rows:
            period = row.get("period")
            dt = self._parse_period_to_date(period)
            if dt is None:
                continue

            price_val = self._extract_price_value(row)
            if price_val is None:
                continue

            records.append({"trade_date": dt, "price": price_val})

        if not records:
            logger.warning("No EIA v2 data parsed for series %s.", self.series_id)
            return pd.DataFrame(columns=["trade_date", "contract", "price"])

        df = pd.DataFrame.from_records(records)
        df = df.sort_values("trade_date")

        # Clip to requested window
        mask = (df["trade_date"] >= start_date) & (df["trade_date"] <= end_date)
        df = df.loc[mask].copy()

        if df.empty:
            logger.warning(
                "EIA v2 series %s returned no dates in requested window.", self.series_id
            )
            return pd.DataFrame(columns=["trade_date", "contract", "price"])

        df["contract"] = "Henry Hub Spot (daily, EIA v2)"

        return df[["trade_date", "contract", "price"]]
