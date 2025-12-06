from __future__ import annotations

from datetime import date, timedelta
import logging

from etl.db import SessionLocal, engine
from etl.models import Base
from etl.extractors.power_entsoe import PowerEntsoeExtractor
from etl.extractors.gas_eia import GasEIAExtractor
from etl.transform import normalise_prices
from etl.load import load_prices


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("commod_etl")


def run_etl(start_date: date, end_date: date) -> None:
    """Run the ETL for power (ENTSO-E) and gas (EIA) for a given date range."""

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    power_extractor = PowerEntsoeExtractor(bidding_zone="DE_LU")
    gas_extractor = GasEIAExtractor(series_id="NG.RNGWHHD.D")  # Henry Hub daily

    with SessionLocal() as session:
        # POWER
        power_raw = power_extractor.fetch_prices(start_date, end_date)
        power_norm = normalise_prices(
            power_raw,
            commodity="POWER",
            source_name=power_extractor.name,
            default_contract="Day-Ahead Baseload",
        )
        load_prices(power_norm, session)

        # GAS
        gas_raw = gas_extractor.fetch_prices(start_date, end_date)
        gas_norm = normalise_prices(
            gas_raw,
            commodity="GAS",
            source_name=gas_extractor.name,
            default_contract="Henry Hub Spot",
        )
        load_prices(gas_norm, session)


if __name__ == "__main__":
    # Example: run for the last 7 days
    today = date.today()
    start = today - timedelta(days=150)
    run_etl(start_date=start, end_date=today)
