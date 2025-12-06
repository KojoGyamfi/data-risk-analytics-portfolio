from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from a .env file if present
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

# Database URL: default to a local SQLite file
DEFAULT_DB_PATH = BASE_DIR / "commod_prices.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# External API credentials
# ENTSO-E Transparency Platform token
ENTSOE_API_TOKEN = os.getenv("ENTSOE_API_TOKEN")

# U.S. EIA Open Data API key
EIA_API_KEY = os.getenv("EIA_API_KEY")

# Simple commodity metadata you can extend later
COMMODITIES = {
    "POWER": {
        "default_region": "DE-LU",   # Example bidding zone
        "unit": "EUR/MWh",
        "currency": "EUR",
    },
    "GAS": {
        "default_region": "US",
        "unit": "USD/MMBtu",
        "currency": "USD",
    },
} 
