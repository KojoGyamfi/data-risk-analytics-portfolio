import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# === Generate Only Weekday Dates ===
def generate_trading_days(start_date, num_days_required):
    dates = []
    current = start_date
    while len(dates) < num_days_required:
        if current.weekday() < 5:  # 0 = Monday, ..., 4 = Friday
            dates.append(current)
        current += timedelta(days=1)
    return dates

# === Generate Sector-Wide Price Drivers ===
def generate_sector_drivers(sectors, num_days):
    return {
        sector: np.cumsum(np.random.normal(0, 1, num_days))
        for sector in sectors
    }

# === Generate Market Data ===
def generate_market_data(tickers, sector_drivers, dates, output_path):
    market_data = []
    num_days = len(dates)

    for ticker, (sector, _) in tickers.items():
        base_price = np.random.uniform(80, 150)
        base_vol = np.random.uniform(0.2, 0.5)
        sector_path = sector_drivers[sector]
        noise = np.random.normal(0, 1, num_days)
        vol_shock = np.random.normal(0, 0.02, num_days)

        spot = base_price + sector_path + 0.5 * noise
        vol = np.clip(
            base_vol + 0.1 * np.sin(np.linspace(0, 3.14, num_days)) + vol_shock,
            0.15, 0.8
        )

        for i, date in enumerate(dates):
            market_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "ticker": ticker,
                "spot_price": round(spot[i], 2),
                "implied_vol": round(vol[i], 4)
            })

    df = pd.DataFrame(market_data)
    df.to_csv(output_path, index=False)
    return df

# === Generate Portfolio Positions ===
def generate_positions(tickers, start_date, num_trades, output_path):
    positions = []
    ticker_list = list(tickers.keys())
    option_types = ["call", "put"]

    for trade_id in range(1, num_trades + 1):
        ticker = np.random.choice(ticker_list)
        sector, region = tickers[ticker]
        position = np.random.choice([-1, 1]) * np.random.randint(10, 200)
        option_type = np.random.choice(option_types)
        maturity_offset = np.random.randint(15, 90)
        maturity_date = (start_date + timedelta(days=maturity_offset)).strftime("%Y-%m-%d")

        positions.append({
            "trade_id": trade_id,
            "ticker": ticker,
            "sector": sector,
            "region": region,
            "option_type": option_type,
            "position": position,
            "delta": round(np.random.uniform(-1.5, 1.5), 3),
            "gamma": round(np.random.uniform(0.01, 0.3), 3),
            "vega": round(np.random.uniform(-1.0, 1.0), 3),
            "theta": round(np.random.uniform(-0.5, 0.5), 3),
            "maturity_date": maturity_date
        })

    df = pd.DataFrame(positions)
    df.to_csv(output_path, index=False)
    return df

# === Simulate Daily Actual P&L ===
def simulate_actual_pnl(positions, market_df, output_path):
    records = []

    for trade in positions:
        ticker = trade["ticker"]
        pos = trade["position"]
        delta = trade["delta"]
        gamma = trade["gamma"]
        vega = trade["vega"]
        theta = trade["theta"]
        trade_id = trade["trade_id"]

        market = market_df[market_df["ticker"] == ticker].copy()
        market["spot_t-1"] = market["spot_price"].shift(1)
        market["vol_t-1"] = market["implied_vol"].shift(1)
        market = market.dropna()

        for _, row in market.iterrows():
            delta_s = row["spot_price"] - row["spot_t-1"]
            delta_vol = row["implied_vol"] - row["vol_t-1"]
            explained = (
                delta * delta_s +
                0.5 * gamma * delta_s**2 +
                vega * delta_vol +
                theta * 1
            ) * pos

            actual = explained + np.random.normal(0, 5)

            records.append({
                "date": row["date"],
                "trade_id": trade_id,
                "actual_pnl": round(actual, 2)
            })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    return df

# === Main Runner ===
def main():
    np.random.seed(42)
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    start_date = datetime(2025, 6, 1)
    num_days = 30
    dates = generate_trading_days(start_date, num_days)

    tickers = {
        "AAPL": ("Tech", "US"), "MSFT": ("Tech", "US"), "AMZN": ("Tech", "US"), "SSNLF": ("Tech", "Asia"),
        "SHEL": ("Energy", "Europe"), "BP": ("Energy", "Europe"), "XOM": ("Energy", "US"),
        "TSLA": ("Auto", "US"), "TM": ("Auto", "Asia"), "MBGYY": ("Auto", "Europe"),
        "HSBC": ("Financials", "Europe"),
        "BABA": ("Consumer", "Asia"), "PG": ("FMCG", "US"), "ULVR": ("FMCG", "Europe"), "KO": ("FMCG", "US"),
        "JNJ": ("Healthcare", "US"), "PFE": ("Healthcare", "US"), "AZN": ("Healthcare", "Europe")
    }

    sectors = set(sector for sector, _ in tickers.values())
    sector_drivers = generate_sector_drivers(sectors, num_days)

    market_df = generate_market_data(tickers, sector_drivers, dates, f"{output_dir}/market_data.csv")
    positions_df = generate_positions(tickers, dates[0], 50, f"{output_dir}/positions.csv")
    simulate_actual_pnl(positions_df.to_dict("records"), market_df, f"{output_dir}/pnl_actuals.csv")

    print("✅ Synthetic data generated (weekdays only) and saved to 'data/'")

# === Entry Point ===
if __name__ == "__main__":
    main()
