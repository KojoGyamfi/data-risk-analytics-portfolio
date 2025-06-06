import pandas as pd

def load_data():
    """Load positions, market data, and actual P&L from CSV files."""
    positions = pd.read_csv("positions.csv")
    market = pd.read_csv("market_data.csv")
    actual_pnl = pd.read_csv("pnl_actuals.csv")
    return positions, market, actual_pnl

def compute_attribution(positions_df, market_df, pnl_df):
    """Compute explained P&L from Greeks and compare to actual P&L."""
    market_t1 = market_df[market_df['date'] == '2025-06-01'].rename(columns={
        'spot_price': 'spot_t1', 'implied_vol': 'vol_t1'
    }).drop(columns=['date'])
    market_t2 = market_df[market_df['date'] == '2025-06-02'].rename(columns={
        'spot_price': 'spot_t2', 'implied_vol': 'vol_t2'
    }).drop(columns=['date'])

    df = positions_df.merge(market_t1, on='ticker').merge(market_t2, on='ticker')
    df['delta_s'] = df['spot_t2'] - df['spot_t1']
    df['delta_vol'] = df['vol_t2'] - df['vol_t1']
    df['delta_pnl'] = df['delta'] * df['delta_s']
    df['gamma_pnl'] = 0.5 * df['gamma'] * df['delta_s'] ** 2
    df['vega_pnl'] = df['vega'] * df['delta_vol']
    df['theta_pnl'] = df['theta'] * 1
    df['explained_pnl_per_unit'] = df['delta_pnl'] + df['gamma_pnl'] + df['vega_pnl'] + df['theta_pnl']
    df['explained_pnl'] = df['explained_pnl_per_unit'] * df['position']
    final_df = df.merge(pnl_df, on='trade_id')
    final_df['residual'] = final_df['actual_pnl'] - final_df['explained_pnl']
    return final_df

def summarize_by_group(df, groupby_col="ticker"):
    """Summarize P&L attribution by a given grouping key (e.g., ticker, instrument_type)."""
    grouped = df.groupby(groupby_col).apply(
        lambda g: pd.Series({
            'Actual P&L': round(g["actual_pnl"].sum(), 2),
            'Explained P&L': round(g["explained_pnl"].sum(), 2),
            'Residual': round(g["residual"].sum(), 2),
            'Delta P&L': round((g["delta_pnl"] * g["position"]).sum(), 2),
            'Gamma P&L': round((g["gamma_pnl"] * g["position"]).sum(), 2),
            'Vega P&L': round((g["vega_pnl"] * g["position"]).sum(), 2),
            'Theta P&L': round((g["theta_pnl"] * g["position"]).sum(), 2)
        })
    ).reset_index()
    return grouped
