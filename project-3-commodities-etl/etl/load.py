from __future__ import annotations

import logging

import pandas as pd
from sqlalchemy.orm import Session

from .models import Price

logger = logging.getLogger(__name__)


def load_prices(df: pd.DataFrame, session: Session) -> int:
    """Insert normalised price rows into the DB.

    Returns the number of rows inserted.
    """
    if df.empty:
        logger.info("No rows to load for this extractor.")
        return 0

    records = [Price(**row) for row in df.to_dict(orient="records")]

    session.add_all(records)
    session.commit()

    inserted = len(records)
    logger.info("Inserted %d price rows.", inserted)
    return inserted
