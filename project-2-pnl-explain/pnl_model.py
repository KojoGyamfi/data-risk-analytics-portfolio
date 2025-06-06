import pandas as pd
import os

def load_data(data_dir="data"):
    positions = pd.read_csv(os.path.join(data_dir, "positions.csv"))
    market = pd.read_csv(os.path.join(data_dir, "market_data.csv"))
    pnl_actuals = pd.read_csv(os.path.join(data_dir, "pnl_actuals.csv"))
    return positions, market, pnl_actuals

def compute_daily_pnl_explained(positions_df, market_df, pnl_df):
    market_df = market_df.sort_values(["ticker", "date"])
    market_df["spot_t-1"] = market_df.groupby("ticker")["spot_price"].shift(1)
    market_df["vol_t-1"] = market_df.groupby("ticker")["implied_vol"].shift(1)
    market_df = market_df.dropna()

    records = []

    for _, trade in positions_df.iterrows():
        trade_id = trade["trade_id"]
        ticker = trade["ticker"]
        pos = trade["position"]
        delta = trade["delta"]
        gamma = trade["gamma"]
        vega = trade["vega"]
        theta = trade["theta"]

        ticker_data = market_df[market_df["ticker"] == ticker].copy()

        for _, row in ticker_data.iterrows():
            date = row["date"]
            delta_s = row["spot_price"] - row["spot_t-1"]
            delta_vol = row["implied_vol"] - row["vol_t-1"]

            delta_pnl = delta * delta_s
            gamma_pnl = 0.5 * gamma * delta_s ** 2
            vega_pnl = vega * delta_vol
            theta_pnl = theta * 1

            explained = (delta_pnl + gamma_pnl + vega_pnl + theta_pnl) * pos

            actual_row = pnl_df[(pnl_df["date"] == date) & (pnl_df["trade_id"] == trade_id)]
            actual_pnl = actual_row["actual_pnl"].values[0] if not actual_row.empty else None

            if actual_pnl is not None:
                records.append({
                    "date": date,
                    "trade_id": trade_id,
                    "ticker": ticker,
                    "sector": trade["sector"],
                    "region": trade["region"],
                    "position": pos,
                    "delta_pnl": round(delta_pnl * pos, 2),
                    "gamma_pnl": round(gamma_pnl * pos, 2),
                    "vega_pnl": round(vega_pnl * pos, 2),
                    "theta_pnl": round(theta_pnl * pos, 2),
                    "explained_pnl": round(explained, 2),
                    "actual_pnl": actual_pnl,
                    "residual": round(actual_pnl - explained, 2)
                })

    return pd.DataFrame(records)

def main():
    data_dir = "data"
    output_file = os.path.join(data_dir, "explained_pnl_timeseries.csv")
    positions_df, market_df, pnl_df = load_data(data_dir)
    explained_df = compute_daily_pnl_explained(positions_df, market_df, pnl_df)
    explained_df.to_csv(output_file, index=False)
    print(f"✅ Multi-day attribution saved to {output_file}")

if __name__ == "__main__":
    main()
