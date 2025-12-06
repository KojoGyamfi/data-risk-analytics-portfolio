# Project 3 – Commodities ETL (Power, LNG, Emissions)

This project implements a small **commodities ETL pipeline** that pulls and
normalises price data for:

- **Power** (European day-ahead prices via ENTSO-E API)
- **LNG / Gas** (Henry Hub spot or LNG-related series via the U.S. EIA API)
- **Emissions** (EU carbon permits via TradingEconomics API)

The ETL loads all prices into a single, normalised `prices` table in a SQL
database (SQLite by default) for downstream analytics or dashboards.

The focus is on:

- A clear, modular ETL design (extract → transform → load)
- Integration with real-world energy/commodities data APIs
- An analytics-friendly schema that can be queried by commodity/region/contract/date

> **Note**: API calls require free registration with each provider and setting
> API keys in a `.env` file. The structure and code are end-to-end; you can
> plug in real credentials to run it against live data.

---

## 1. Architecture Overview

### 1.1 High-level flow

1. **Extract**  
   - `PowerEntsoeExtractor` (ENTSO-E day-ahead prices)
   - `LNGEIAExtractor` (EIA natural gas / LNG-related series)
   - `EmissionsTradingEconomicsExtractor` (EU carbon permits from TradingEconomics)

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
│  │   ├─ power_entsoe.py    # ENTSO-E power prices extractor
│  │   ├─ lng_eia.py         # EIA LNG/gas price extractor
│  │   └─ emissions_te.py    # TradingEconomics emissions extractor
│  ├─ transform.py           # normalise to canonical schema
│  └─ load.py                # load into DB
├─ pipelines/
│  └─ daily_prices.py        # entry point: run ETL for a date range
├─ data_samples/             # (placeholder for any sample CSVs you may add)
├─ .env.example              # template for API keys and DB URL
├─ requirements.txt
└─ README.md
```

---

## 3. Data Model

The ETL writes into a single table `prices` (see `etl/models.py`):

- `commodity` – `"POWER"`, `"LNG"`, `"EMISSIONS"`
- `region` – e.g. `"DE-LU"`, `"US"`, `"EU ETS"`
- `contract` – e.g. `"Day-Ahead"`, `"Henry Hub Spot"`, `"EU Carbon Permits"`
- `trade_date` – date of the price (daily / monthly etc.)
- `price` – numeric price
- `currency` – e.g. `"EUR"`, `"USD"`
- `unit` – e.g. `"EUR/MWh"`, `"USD/MMBtu"`, `"EUR/tCO2e"`
- `source` – `"ENTSOE_API"`, `"EIA_API"`, `"TE_API"`
- `created_at` – timestamp when the ETL inserted the row

This schema is deliberately simple and analytics-friendly. You can easily:

- Slice by commodity/region/date,
- Compute simple spreads (e.g. power vs emissions),
- Feed downstream BI tools (Power BI, Tableau, etc.).

---

## 4. External APIs Used

All of these have **free access tiers** suitable for this project.

### 4.1 ENTSO-E Transparency Platform (Power)

- Provides European electricity market data including **day-ahead prices**.
- Requires registration and an API token on the Transparency Platform.
- This project uses:
  - `PowerEntsoeExtractor` with a configured `bidding_zone` (e.g. `"DE-LU"`).

You must:

1. Register on https://transparency.entsoe.eu and request "Restful API access".
2. Set `ENTSOE_API_TOKEN` in your `.env`.

> The provided code contains a placeholder XML parser. For production use you
> would implement full XML parsing of the ENTSO-E response here.

### 4.2 U.S. EIA Open Data API (LNG / gas)

- Provides free access to U.S. energy series.
- We use it as a proxy for LNG/gas prices, e.g. **Henry Hub spot**:
  - Example series ID: `NG.RNGWHHD.D` (Henry Hub daily prices).
- You must:
  1. Register at https://www.eia.gov/opendata/ to obtain an API key.
  2. Set `EIA_API_KEY` in your `.env`.

`LNGEIAExtractor`:

- Calls `https://api.eia.gov/series/` with your API key and `series_id`,
- Parses `[date, value]` pairs into `trade_date`, `price`.

### 4.3 TradingEconomics API (Emissions)

- Provides **EU Carbon Permits** prices (symbol `EECXM:IND`).
- Requires free API credentials (client + secret).
- You must:
  1. Create an account and get `TE_CLIENT` and `TE_SECRET`.
  2. Set them in your `.env`.

`EmissionsTradingEconomicsExtractor`:

- Calls `https://api.tradingeconomics.com/markets/historical`,
- Filters by `symbol="EECXM:IND"`,
- Extracts `Date` and `Close` → `trade_date`, `price`.

---

## 5. Setup & Usage

### 5.1 Install dependencies

From the project root (`project-3-commod-etl`):

```bash
pip install -r requirements.txt
```

### 5.2 Configure environment

1. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Fill in:

   - `ENTSOE_API_TOKEN`
   - `EIA_API_KEY`
   - `TE_CLIENT`
   - `TE_SECRET`
   - (Optional) `DATABASE_URL` if you don't want the default SQLite file.

### 5.3 Run the ETL

From the project root:

```bash
python -m pipelines.daily_prices
```

By default, it runs the ETL for the last 7 days. You can modify
`daily_prices.py` to accept CLI arguments or a specific date range.

If everything is configured correctly, you should see logs such as:

- ENTSO-E / EIA / TradingEconomics requests,
- Number of rows inserted for each commodity.

The resulting DB file (if using SQLite) will be:

```text
commod_prices.db
```

in the project root.

---

## 6. Visualisation (Next Step)

This project focuses on the ETL architecture and integration with real-world
APIs. It is straightforward to add:

- A **Jupyter notebook** that:
  - Connects to the DB,
  - Plots price histories by commodity/region/contract,
  - Computes simple spreads or correlations.
- Or a small **Streamlit app** that:
  - Lets you choose commodity/region/date range,
  - Shows time series charts and simple analytics.

These can be added on top of the `prices` table without changing the ETL core.

---

## 7. What This Project Demonstrates

From a **quant / data / risk analytics** perspective, this ETL shows:

- Understanding of **energy & carbon markets** data structures.
- Ability to design a clean **Extract–Transform–Load** pipeline:
  - Modular extractors per data source,
  - A unified transform layer,
  - Normalised schema in a relational DB.
- Practical integration with:
  - A European market infrastructure API (ENTSO-E),
  - A U.S. government open data API (EIA),
  - A market data API (TradingEconomics).
- Code that is:
  - Reasonably production-like in structure,
  - Easy to extend (new commodities, new APIs),
  - Ready to feed downstream analytics or dashboards.
