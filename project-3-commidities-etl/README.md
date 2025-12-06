# Project 3 – Commodities ETL & Dashboard (ENTSO-E Power + EIA Gas)

This project implements a **commodities ETL pipeline + Streamlit dashboard** for:

- **European power** – day-ahead prices from the ENTSO-E Transparency Platform  
- **U.S. natural gas** – Henry Hub spot prices from the EIA Open Data API (v2)

The ETL:

1. Pulls data from both APIs,
2. Normalises it into a single `prices` table in a SQL database (SQLite by default),
3. Exposes it via a small **Streamlit app** for quick visual analysis.

The focus is on:

- A clean, modular **Extract → Transform → Load** design,
- Integration with **real energy market APIs** (ENTSO-E + EIA v2),
- An analytics-friendly schema that can feed notebooks, BI tools, or further quant work,
- A lightweight dashboard that shows how the data is actually used.

---

## 1. Data Sources

### 1.1 ENTSO-E Transparency Platform (Power)

- Provides European electricity market data, including **day-ahead prices** by bidding zone.
- This project uses:
  - `entsoe-py` (`EntsoePandasClient`) with a configured `bidding_zone` (default: `DE_LU`).
  - The **day-ahead hourly prices**, aggregated to **daily average** per `trade_date`.

You must:

1. Register at the ENTSO-E Transparency Platform and request **RESTful API access**.
2. Set `ENTSOE_API_TOKEN` in your `.env`.

Extractor:

- `etl/extractors/power_entsoe.py` → `PowerEntsoeExtractor`
  - Calls `query_day_ahead_prices(...)`,
  - Aggregates hourly prices → daily average price per date,
  - Returns a tidy `DataFrame` with `trade_date`, `contract`, `price`.

### 1.2 EIA Open Data API v2 (Gas)

- Provides programmatic access to U.S. energy time series.
- This project uses **EIA API v2** via the backward-compat endpoint:

  - Endpoint: `https://api.eia.gov/v2/seriesid/NG.RNGWHHD.D`
  - Series: `NG.RNGWHHD.D` (Henry Hub **daily** spot gas price).

You must:

1. Register for an EIA API key at <https://www.eia.gov/opendata/>.
2. Set `EIA_API_KEY` in your `.env`.

Extractor:

- `etl/extractors/gas_eia.py` → `GasEIAExtractor`
  - Calls `https://api.eia.gov/v2/seriesid/NG.RNGWHHD.D?api_key=...`,
  - Parses the v2 JSON (`response.data[*].period`, `value`),
  - Converts the `period` field to `trade_date` (Python `date`),
  - Filters to the requested date window,
  - Returns `trade_date`, `contract`, `price`.

---

## 2. Architecture Overview

### 2.1 High-level flow

1. **Extract**
   - `PowerEntsoeExtractor` (ENTSO-E day-ahead prices, hourly → daily)
   - `GasEIAExtractor` (EIA v2 Henry Hub daily spot)

2. **Transform**
   - `etl/transform.py`:
     - Converts each source’s output into a **canonical schema**:

       ```text
       commodity, region, contract, trade_date,
       price, currency, unit, source, created_at
       ```

     - Uses `etl.config.COMMODITIES` to attach default region / currency / unit.

3. **Load**
   - `etl/load.py`:
     - Inserts the normalised rows into the `prices` table via SQLAlchemy.

4. **Visualise**
   - `streamlit_app.py`:
     - Reads from `commod_prices.db`,
     - Provides filters (commodity + date range),
     - Plots:
       - Raw price levels (with units),
       - Normalised indices (start = 100),
     - Shows a data preview and summary stats.

### 2.2 Project Structure

```text
project-3-commidities-etl/
├─ etl/
│  ├─ __init__.py
│  ├─ config.py              # config (DB URL, API keys, commodity metadata)
│  ├─ db.py                  # SQLAlchemy engine + session
│  ├─ models.py              # ORM model: Price table
│  ├─ extractors/
│  │   ├─ __init__.py
│  │   ├─ base.py            # BaseExtractor interface
│  │   ├─ power_entsoe.py    # ENTSO-E power prices extractor (entsoe-py)
│  │   └─ gas_eia.py         # EIA v2 Henry Hub gas extractor
│  ├─ transform.py           # normalise to canonical schema
│  └─ load.py                # load into DB
├─ pipelines/
│  └─ daily_prices.py        # entry point: run ETL for a date range
├─ streamlit_app.py          # Streamlit dashboard (prices + indices + stats)
├─ .env.example              # template for API keys and DB URL
├─ requirements.txt
└─ README.md
