import pandas as pd
import numpy as np

def generate_market_data(tickers, dates):
    market_data = []
    for ticker in tickers:
        spot_t1 = np.random.uniform(100, 300)
        spot_t2 = spot_t1 * np.random.uniform(0.98, 1.05)
        vol_t1 = np.random.uniform(0.2, 0.4)
        vol_t2 = vol_t1 * np.random.uniform(0.95, 1.1)
        market_data.extend([
            {'date': dates[0], 'ticker': ticker, 'spot_price': round(spot_t1, 2), 'implied_vol': round(vol_t1, 4)},
            {'date': dates[1], 'ticker': ticker, 'spot_price': round(spot_t2, 2), 'implied_vol': round(vol_t2, 4)}
        ])
    return pd.DataFrame(market_data)

def generate_positions(tickers, market_df, n=20):
    instrument_types = ['call', 'put']
    positions = []
    for i in range(n):
        ticker = np.random.choice(tickers)
        instrument = np.random.choice(instrument_types)
        position = np.random.randint(-200, 200)
        delta = np.random.uniform(-1, 1)
        gamma = np.random.uniform(0.01, 0.05)
        vega = np.random.uniform(0.05, 0.2)
        theta = np.random.uniform(-0.05, 0)
        price = np.random.uniform(2, 10)
        implied_vol = market_df[(market_df['ticker'] == ticker) & (market_df['date'] == '2025-06-01')]['implied_vol'].values[0]
        positions.append({
            'trade_id': f'T{i+1}',
            'date': '2025-06-01',
            'ticker': ticker,
            'instrument_type': instrument,
            'position': position,
            'delta': round(delta, 4),
            'gamma': round(gamma, 4),
            'vega': round(vega, 4),
            'theta': round(theta, 4),
            'price_t-1': round(price, 2),
            'implied_vol_t-1': round(implied_vol, 4)
        })
    return pd.DataFrame(positions)

def generate_actual_pnl(positions_df, market_df):
    pnl_data = []
    for _, row in positions_df.iterrows():
        spot_prices = market_df[market_df['ticker'] == row['ticker']].sort_values(by='date')
        delta_pnl = row['delta'] * (spot_prices.iloc[1]['spot_price'] - spot_prices.iloc[0]['spot_price'])
        gamma_pnl = 0.5 * row['gamma'] * (spot_prices.iloc[1]['spot_price'] - spot_prices.iloc[0]['spot_price'])**2
        vega_pnl = row['vega'] * (spot_prices.iloc[1]['implied_vol'] - spot_prices.iloc[0]['implied_vol'])
        theta_pnl = row['theta'] * 1
        noise = np.random.normal(0, 2)
        actual_pnl = (delta_pnl + gamma_pnl + vega_pnl + theta_pnl + noise) * row['position']
        pnl_data.append({
            'trade_id': row['trade_id'],
            'date': '2025-06-02',
            'actual_pnl': round(actual_pnl, 2)
        })
    return pd.DataFrame(pnl_data)

def generate_all_data():
    np.random.seed(42)
    tickers = ['AAPL', 'TSLA', 'SPY', 'MSFT', 'NVDA']
    dates = ['2025-06-01', '2025-06-02']

    market_df = generate_market_data(tickers, dates)
    positions_df = generate_positions(tickers, market_df)
    pnl_df = generate_actual_pnl(positions_df, market_df)

    return market_df, positions_df, pnl_df

# Save to CSV
market_df, positions_df, pnl_df = generate_all_data()
market_df.to_csv("/mnt/data/market_data.csv", index=False)
positions_df.to_csv("/mnt/data/positions.csv", index=False)
pnl_df.to_csv("/mnt/data/pnl_actuals.csv", index=False)

