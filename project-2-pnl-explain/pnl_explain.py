import pandas as pd

def load_data():
    """Load positions, market data, and actual P&L from CSV files."""
    positions = pd.read_csv("positions.csv")
    market = pd.read_csv("market_data.csv")
    actual_pnl = pd.read_csv("pnl_actuals.csv")
    return positions, market, actual_pnl

def compute_attribution(positions_df, market_df, pnl_df):
    """Compute explained P&L from Greeks and compare to actual P&L."""

    # Extract market data for t-1 and t
    market_t1 = market_df[market_df['date'] == '2025-06-01'].rename(columns={
        'spot_price': 'spot_t1',
        'implied_vol': 'vol_t1'
    }).drop(columns=['date'])

    market_t2 = market_df[market_df['date'] == '2025-06-02'].rename(columns={
        'spot_price': 'spot_t2',
        'implied_vol': 'vol_t2'
    }).drop(columns=['date'])

    # Merge market data with positions
    df = positions_df.merge(market_t1, on='ticker').merge(market_t2, on='ticker')

    # Market moves
    df['delta_s'] = df['spot_t2'] - df['spot_t1']
    df['delta_vol'] = df['vol_t2'] - df['vol_t1']

    # Calculate P&L components
    df['delta_pnl'] = df['delta'] * df['delta_s']
    df['gamma_pnl'] = 0.5 * df['gamma'] * df['delta_s'] ** 2
    df['vega_pnl'] = df['vega'] * df['delta_vol']
    df['theta_pnl'] = df['theta'] * 1  # Assuming 1 day

    # Combine into explained P&L per unit
    df['explained_pnl_per_unit'] = (
        df['delta_pnl'] +
        df['gamma_pnl'] +
        df['vega_pnl'] +
        df['theta_pnl']
    )

    # Multiply by position size
    df['explained_pnl'] = df['explained_pnl_per_unit'] * df['position']

    # Merge with actual P&L
    df = df.merge(pnl_df, on='trade_id')
    df['residual'] = df['actual_pnl'] - df['explained_pnl']

    # Output columns
    output = df[[
        'trade_id', 'ticker', 'instrument_type', 'position',
        'delta_pnl', 'gamma_pnl', 'vega_pnl', 'theta_pnl',
        'explained_pnl', 'actual_pnl', 'residual'
    ]].round(2)

    return output

def main():
    positions, market, actual_pnl = load_data()
    explained_df = compute_attribution(positions, market, actual_pnl)
    explained_df.to_csv("explained_pnl_output.csv", index=False)
    print("✅ Attribution complete. Output saved to explained_pnl_output.csv")

if __name__ == "__main__":
    main()
