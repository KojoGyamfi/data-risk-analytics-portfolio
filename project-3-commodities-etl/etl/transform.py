from __future__ import annotations

from datetime import datetime
from typing import Literal

import pandas as pd

from .config import COMMODITIES


def normalise_prices(
    raw_df: pd.DataFrame,
    commodity: Literal["POWER", "GAS"],
    source_name: str,
    default_contract: str,
) -> pd.DataFrame:
    """Transform a raw source-specific DataFrame into the canonical schema.

    Output columns:
        commodity, region, contract, trade_date,
        price, currency, unit, source, created_at
    """

    if raw_df.empty:
        return raw_df.copy()

    meta = COMMODITIES[commodity]

    df = raw_df.copy()

    if "trade_date" not in df.columns:
        raise ValueError("Expected 'trade_date' column in raw_df.")
    if "price" not in df.columns:
        raise ValueError("Expected 'price' column in raw_df.")

    # If 'contract' is missing, default to a single label for the extractor.
    if "contract" not in df.columns:
        df["contract"] = default_contract

    df["commodity"] = commodity
    df["region"] = meta["default_region"]
    df["currency"] = meta["currency"]
    df["unit"] = meta["unit"]
    df["source"] = source_name
    df["created_at"] = datetime.utcnow()

    # Ensure trade_date is date type
    if pd.api.types.is_datetime64_any_dtype(df["trade_date"]):
        df["trade_date"] = df["trade_date"].dt.date

    cols = [
        "commodity",
        "region",
        "contract",
        "trade_date",
        "price",
        "currency",
        "unit",
        "source",
        "created_at",
    ]

    return df[cols].copy()
