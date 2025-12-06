from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Price(Base):
    """
    Normalised price record for any commodity.

    This keeps the schema deliberately simple and analytics-friendly.
    """

    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)

    commodity = Column(String(50), nullable=False)   # e.g. "POWER", "LNG", "EMISSIONS"
    region = Column(String(50), nullable=False)      # e.g. "DE-LU", "US", "EU ETS"
    contract = Column(String(100), nullable=False)   # e.g. "Day-Ahead", "Front-Month", "DEC-25"
    trade_date = Column(Date, nullable=False)        # trade / delivery date
    price = Column(Float, nullable=False)

    currency = Column(String(10), nullable=False)    # e.g. "EUR", "USD"
    unit = Column(String(50), nullable=False)        # e.g. "EUR/MWh", "USD/MMBtu"

    source = Column(String(100), nullable=False)     # e.g. "ENTSOE_API", "EIA_API", "TE_API", "CSV_DEMO"
    created_at = Column(DateTime, nullable=False)    # ETL insertion time


def create_all(engine) -> None:
    """Create all tables on the given engine."""
    Base.metadata.create_all(bind=engine)
