from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import streamlit as st

from etl.config import COMMODITIES  # to get units/currency per commodity


DB_PATH = Path(__file__).resolve().parent / "commod_prices.db"


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load all prices from the SQLite DB into a DataFrame."""
    if not DB_PATH.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(
            """
            SELECT
                commodity,
                region,
                contract,
                trade_date,
                price,
                currency,
                unit,
                source,
                created_at
            FROM prices
            ORDER BY trade_date, commodity
            """,
            conn,
        )
    finally:
        conn.close()

    if df.empty:
        return df

    # Ensure trade_date is datetime64[ns] for plotting
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def _build_units_caption(columns: List[str]) -> str:
    """Build a human-readable units string for selected commodities."""
    parts: List[str] = []
    for c in columns:
        meta = COMMODITIES.get(c)
        if not meta:
            parts.append(f"{c.title()}: [unit unknown]")
            continue
        unit = meta.get("unit", "")
        currency = meta.get("currency", "")
        if unit and currency:
            parts.append(f"{c.title()}: {unit} ({currency})")
        elif unit:
            parts.append(f"{c.title()}: {unit}")
        else:
            parts.append(c.title())
    return " | ".join(parts)


def main() -> None:
    st.set_page_config(
        page_title="Commodities ETL – Power & Gas Prices",
        layout="wide",
    )

    st.title("Commodities ETL – Power & Gas Pricing Dashboard")
    st.caption(
        "Data from ENTSO-E (POWER) and EIA v2 (GAS: Henry Hub Spot), "
        "loaded via the ETL pipeline in this project."
    )

    df = load_data()

    if df.empty:
        st.warning(
            "No data found in `commod_prices.db`.\n\n"
            "Run the ETL first:\n\n"
            "```bash\npython -m pipelines.daily_prices\n```"
        )
        return

    # Sidebar filters
    st.sidebar.header("Filters")

    available_commodities: List[str] = sorted(df["commodity"].unique().tolist())
    selected_commodities = st.sidebar.multiselect(
        "Commodity",
        options=available_commodities,
        default=available_commodities,
    )

    if not selected_commodities:
        st.info("Select at least one commodity to view data.")
        return

    df = df[df["commodity"].isin(selected_commodities)]

    # Date range selector based on data
    min_date = df["trade_date"].min().date()
    max_date = df["trade_date"].max().date()

    date_range: Tuple = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # `date_input` can return a single date or tuple depending on UI state
    if isinstance(date_range, tuple):
        start_date, end_date = date_range
    else:
        start_date, end_date = date_range, date_range

    # Filter by selected date range
    mask = (df["trade_date"].dt.date >= start_date) & (
        df["trade_date"].dt.date <= end_date
    )
    df = df.loc[mask].copy()

    if df.empty:
        st.warning("No rows found for the selected filters.")
        return

    # Main charts
    st.subheader("Price Time Series (Raw Levels)")

    # Pivot for time series chart: one column per commodity (raw names)
    pivot_raw = (
        df.pivot_table(
            index="trade_date",
            columns="commodity",
            values="price",
            aggfunc="first",
        )
        .sort_index()
    )

    # Build nicer display names with units, e.g. "Power (EUR/MWh)"
    label_map = {}
    for c in pivot_raw.columns:
        meta = COMMODITIES.get(c)
        if meta:
            unit = meta.get("unit", "")
            if unit:
                label_map[c] = f"{c.title()} ({unit})"
            else:
                label_map[c] = c.title()
        else:
            label_map[c] = c.title()

    pivot_display = pivot_raw.rename(columns=label_map)

    st.line_chart(pivot_display)

    # Caption with units per commodity
    units_caption = _build_units_caption(list(pivot_raw.columns))
    if units_caption:
        st.caption(f"Units by commodity: {units_caption}")

    # Normalised index chart (start = 100)
    if pivot_display.shape[1] >= 1:
        st.subheader("Normalised Price Index (start = 100)")

        # Drop rows with all NaNs
        norm = pivot_display.dropna(how="all").copy()

        if not norm.empty:
            # For each series, divide by its value at the first date where it exists,
            # then multiply by 100 to get an index (unitless)
            first_valid = norm.iloc[0]
            norm_index = norm.divide(first_valid) * 100.0

            st.line_chart(norm_index)
            st.caption(
                "Each series is rebased to 100 at the first date in the selected range "
                "where it has data. Values are unitless indices showing relative moves."
            )
        else:
            st.info(
                "Not enough overlapping data to build a normalised index "
                "for the selected filters."
            )

    # Data preview
    st.subheader("Data Preview")

    # Pretty column names for table display
    display_df = df.rename(
        columns={
            "commodity": "Commodity",
            "region": "Region",
            "contract": "Contract",
            "trade_date": "Trade Date",
            "price": "Price",
            "currency": "Currency",
            "unit": "Unit",
            "source": "Source",
            "created_at": "Created At",
        }
    )

    with st.expander("Show filtered data"):
        st.dataframe(
            display_df.sort_values(["Trade Date", "Commodity"]),
            use_container_width=True,
        )

    # Summary stats
    st.subheader("Summary Stats by Commodity")

    summary = (
        df.groupby("commodity")
        .agg(
            first_date=("trade_date", "min"),
            last_date=("trade_date", "max"),
            count=("price", "count"),
            min_price=("price", "min"),
            max_price=("price", "max"),
            mean_price=("price", "mean"),
            unit=("unit", "first"),
            currency=("currency", "first"),
        )
        .reset_index()
    )

    summary_display = summary.rename(
        columns={
            "commodity": "Commodity",
            "first_date": "First Date",
            "last_date": "Last Date",
            "count": "Row Count",
            "min_price": "Min Price",
            "max_price": "Max Price",
            "mean_price": "Avg Price",
            "unit": "Unit",
            "currency": "Currency",
        }
    )

    st.dataframe(summary_display, use_container_width=True)
    st.caption(
        "Summary statistics are computed per commodity in their native units "
        "(e.g. Power in EUR/MWh, Gas in USD/MMBtu)."
    )


if __name__ == "__main__":
    main()
