# Project 3 – Commodities ETL (ENTSO-E Power + EIA Gas)

This project implements a **commodities ETL pipeline** that pulls and
normalises price data for:

- **European power** (day-ahead prices via ENTSO-E API, using `entsoe-py`)
- **U.S. natural gas** (Henry Hub spot via the U.S. EIA Open Data API)

The ETL loads all prices into a single, normalised `prices` table in a SQL
database (SQLite by default) for downstream analytics or dashboards.

The focus is on:

- A clear, modular ETL design (extract → transform → load)
- Integration with **two real-world energy data APIs** (ENTSO-E + EIA)
- An analytics-friendly schema that can be queried by commodity/region/contract/date

> API calls require free registration with ENTSO-E and EIA and setting
> API keys in a `.env` file.

---

## 1. Architecture Overview

### 1.1 High-level flow

1. **Extract**
   - `PowerEntsoeExtractor` (ENTSO-E day-ahead prices)
   - `GasEIAExtractor` (EIA Henry Hub spot series)

2. **Transform**
   - Convert each raw source format into a **canonical schema**:
     - `commodity`, `region`, `contract`, `trade_date`,
       `price`, `currency`, `unit`, `source`, `created_at`.

3. **Load**
   - Insert rows into a `prices` table via SQLAlchemy.

Everything is orchestrated by `pipelines/daily_prices.py`.

---

## 2. Project Structure

```text
project-3-commod-etl/
├─ etl/
│  ├─ __init__.py
│  ├─ config.py              # config (DB URL, API keys, commodity metadata)
│  ├─ db.py                  # SQLAlchemy engine + session
│  ├─ models.py              # ORM model: Price table
│  ├─ extractors/
│  │   ├─ __init__.py
│  │   ├─ base.py            # BaseExtractor interface
│  │   ├─ power_entsoe.py    # ENTSO-E power prices extractor (entsoe-py)
│  │   └─ gas_eia.py         # EIA gas price extractor (Henry Hub)
│  ├─ transform.py           # normalise to canonical schema
│  └─ load.py                # load into DB
├─ pipelines/
│  └─ daily_prices.py        # entry point: run ETL for a date range
├─ data_samples/             # (placeholder if you later add CSV-based demos)
├─ .env.example              # template for API keys and DB URL
├─ requirements.txt
└─ README.md
```

---

## 3. Data Model

The ETL writes into a single table `prices` (see `etl/models.py`):

- `commodity` – `"POWER"` or `"GAS"`
- `region` – e.g. `"DE-LU"`, `"US"`
- `contract` – e.g. `"Day-Ahead Baseload"`, `"Henry Hub Spot"`
- `trade_date` – date of the price (daily)
- `price` – numeric price
- `currency` – e.g. `"EUR"`, `"USD"`
- `unit` – e.g. `"EUR/MWh"`, `"USD/MMBtu"`
- `source` – `"ENTSOE_API"`, `"EIA_API"`
- `created_at` – timestamp when the ETL inserted the row

This schema is deliberately simple and analytics-friendly. You can:

- Slice by commodity/region/date,
- Compute simple spreads,
- Feed downstream BI tools (Power BI, Tableau, etc.).

---

## 4. External APIs Used

### 4.1 ENTSO-E Transparency Platform (Power)

- Provides European electricity market data including **day-ahead prices**.
- Requires registration and an API token on the Transparency Platform.
- This project uses:
  - `PowerEntsoeExtractor` with a configured `bidding_zone` (default: `"DE-LU"`),
  - the `entsoe-py` Python client.

You must:

1. Register on https://transparency.entsoe.eu and request "Restful API access".
2. Set `ENTSOE_API_TOKEN` in your `.env`.

`PowerEntsoeExtractor`:

- Calls `EntsoePandasClient.query_day_ahead_prices(...)`,
- Receives hourly prices,
- Aggregates them to **daily average** prices per `trade_date`.

### 4.2 U.S. EIA Open Data API (Gas)

- Provides free access to U.S. energy series.
- We use it for **Henry Hub natural gas spot prices**:
  - Default series ID: `NG.RNGWHHD.D` (daily prices).
- You must:
  1. Register at https://www.eia.gov/opendata/ to obtain an API key.
  2. Set `EIA_API_KEY` in your `.env`.

`GasEIAExtractor`:

- Calls `https://api.eia.gov/series/` with your API key and `series_id`,
- Parses `[date, value]` pairs into `trade_date`, `price`,
- Supports daily (`YYYYMMDD`) and monthly (`YYYYMM`) frequencies.

---

## 5. Setup & Usage

### 5.1 Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

### 5.2 Configure environment


1. Fill in `.env`:

   - `ENTSOE_API_TOKEN`
   - `EIA_API_KEY`
   - (Optional) `DATABASE_URL` if you don't want the default SQLite file.

### 5.3 Run the ETL

From the project root:

```bash
python -m pipelines.daily_prices
```

By default, it runs the ETL for the last 7 days. You can modify
`daily_prices.py` to accept CLI arguments or a specific date range.

If everything is configured correctly, you should see logs such as:

- ENTSO-E and EIA requests,
- Number of rows inserted for power and gas.

The resulting DB file (if using SQLite) will be:

```text
commod_prices.db
```

in the project root.

---

## 6. Visualisation (Next Step)

This project focuses on the ETL architecture and API integration. It is
straightforward to add:

- A **Jupyter notebook** that:
  - Connects to the DB,
  - Plots price histories for POWER and GAS,
  - Computes simple spreads or correlations.
- Or a small **Streamlit app** that:
  - Lets you choose commodity/region/date range,
  - Shows time series charts and simple analytics.

These can be added on top of the `prices` table without changing the ETL core.

---

## 7. What This Project Demonstrates

From a **quant / data / risk analytics** perspective, this ETL shows:

- Understanding of **energy markets data** (power + gas benchmarks).
- Ability to design a clean **Extract–Transform–Load** pipeline:
  - Modular extractors per data source,
  - A unified transform layer,
  - Normalised schema in a relational DB.
- Practical integration with:
  - A European market infrastructure API (ENTSO-E via `entsoe-py`),
  - A U.S. government open data API (EIA).
- Code that is:
  - Reasonably production-like in structure,
  - Easy to extend (new commodities, new APIs),
  - Ready to feed downstream analytics or dashboards.
