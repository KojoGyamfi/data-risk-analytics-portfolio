from __future__ import annotations

from datetime import date, timedelta
import logging

from etl.db import SessionLocal, engine
from etl.models import Base
from etl.extractors.power_entsoe import PowerEntsoeExtractor
from etl.extractors.lng_eia import LNGEIAExtractor
from etl.extractors.emissions_te import EmissionsTradingEconomicsExtractor
from etl.transform import normalise_prices
from etl.load import load_prices


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("commod_etl")


def run_etl(start_date: date, end_date: date) -> None:
    """Run the full ETL for power, LNG, and emissions for a given date range."""

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Instantiate extractors (configure as desired)
    power_extractor = PowerEntsoeExtractor(bidding_zone="DE-LU")
    lng_extractor = LNGEIAExtractor(series_id="NG.RNGWHHD.D")  # Henry Hub daily
    emissions_extractor = EmissionsTradingEconomicsExtractor(symbol="EECXM:IND")

    with SessionLocal() as session:
        # POWER
        power_raw = power_extractor.fetch_prices(start_date, end_date)
        power_norm = normalise_prices(
            power_raw,
            commodity="POWER",
            source_name=power_extractor.name,
            default_contract="Day-Ahead",
        )
        load_prices(power_norm, session)

        # LNG
        lng_raw = lng_extractor.fetch_prices(start_date, end_date)
        lng_norm = normalise_prices(
            lng_raw,
            commodity="LNG",
            source_name=lng_extractor.name,
            default_contract="Henry Hub Spot",
        )
        load_prices(lng_norm, session)

        # EMISSIONS
        emissions_raw = emissions_extractor.fetch_prices(start_date, end_date)
        emissions_norm = normalise_prices(
            emissions_raw,
            commodity="EMISSIONS",
            source_name=emissions_extractor.name,
            default_contract="EU Carbon Permits",
        )
        load_prices(emissions_norm, session)


if __name__ == "__main__":
    # Example: run for the last 7 days
    today = date.today()
    start = today - timedelta(days=7)
    run_etl(start_date=start, end_date=today)
