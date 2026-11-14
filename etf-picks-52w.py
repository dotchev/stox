"""Save the 52-week return stats of the ETF picks in stocks-52w.ipynb to
data/etf-picks-*.csv, over three periods: the weekly history common to all
symbols, 3 years and 5 years. In the 3y and 5y files a symbol with less
history than the period gets empty gmean, std and sharpe.
"""
import pandas as pd
from scipy.stats import gmean
from yfetch import get_weekly_history, get_stock_name, get_stock_currency

symbols = [
    'SPMO',  # Invesco S&P 500 Momentum ETF
    'LVHI',  # Franklin International Low Volatility High Dividend Index ETF
    'SPYM',  # State Street SPDR Portfolio S&P 500 ETF
    'SPYG',  # State Street SPDR Portfolio S&P 500 Growth ETF
    'QQQ',  # Invesco QQQ Trust
    'SMH',  # VanEck Semiconductor ETF
    'MAGS',  # Roundhill Magnificent Seven ETF
    'FNGS',  # MicroSectors FANG+ ETN
    'QTOP',  # iShares Nasdaq Top 30 Stocks ETF
    'TOPT',  # iShares Top 20 U.S. Stocks ETF
    'XLG',  # Invesco S&P 500 Top 50 ETF
    'MGK',  # Vanguard Morningstar Mega Cap Growth ETF
    'USD',  # ProShares Ultra Semiconductors
    'TDIV.AS',  # VanEck Morningstar Developed Markets Dividend Leaders UCITS ETF
    'CHIP.PA',  # Amundi MSCI Semiconductors UCITS ETF Acc
    '4GLD.DE',  # Xetra-Gold
    'JEDI.DE',  # VanEck Space Innovators UCITS ETF A USD Acc
    'IWMO.MI',  # iShares Edge MSCI World Momentum Factor UCITS ETF USD (Acc) - also IS3R.DE
    'XDEM.DE',  # Xtrackers MSCI World Momentum UCITS ETF 1C
    'IS3Q.DE',  # iShares Edge MSCI World Quality Factor UCITS ETF USD (Acc)
    'AIFS.DE',  # iShares AI Infrastructure UCITS ETF USD (Acc)
    'QTOP.AS',  # iShares VII PLC - iShares Nasdaq 100 Top 30 UCITS ETF USD (Acc)
    'XWEM.DE',  # Xtrackers MSCI World Momentum ESG UCITS ETF 1C
    'QDVA.DE',  # iShares Edge MSCI USA Momentum Factor UCITS ETF USD (Acc)
    'WMSE.DE',  # Amundi MSCI World Momentum Screened Factor UCITS ETF USD Acc
    'FTGM.DE',  # First Trust US Momentum UCITS ETF Class A USD Acc
    'CBUH.DE',  # iShares MSCI World Momentum Factor Advanced UCITS ETF USD (Acc)
    'IWDA.AS',  # iShares Core MSCI World UCITS ETF USD (Acc)
    'VHVE.MI',  # Vanguard FTSE Developed World UCITS ETF USD Accumulation
    'VWCE.DE',  # Vanguard FTSE All-World UCITS ETF USD Accumulation
    'IUSQ.DE',  # iShares MSCI All Country World UCITS ETF USD Acc
    'SPYI.DE',  # State Street SPDR MSCI All Country World Investable Market UCITS ETF
    'XAIX.DE',  # Xtrackers Artificial Intelligence & Big Data UCITS ETF 1C
    'TSWE.DE',  # VanEck World Equal Weight Screened UCITS ETF
    'IBCZ.DE',  # iShares STOXX World Equity Multifactor UCITS ETF USD (Acc)
    'LYY0.DE',  # Amundi MSCI All Country World Swap UCITS ETF EUR Acc
]

weeks = 52
risk_free_return = 0.04  # 4%


def load_histories():
    """Weekly USD history per symbol; 5y covers all the periods."""
    histories = {}
    for symbol in symbols:
        history = get_weekly_history(symbol, period='5y', cache_days=2, currency='USD')
        if history.empty:
            raise RuntimeError(f'No history for {symbol}')
        histories[symbol] = history
    return histories


def crunch(histories, history_weeks):
    rows = []
    for symbol, history in histories.items():
        history = history.tail(history_weeks)
        if len(history) < history_weeks:
            gmean_change = std = float('nan')
        else:
            changes = history.Close.pct_change(periods=weeks, fill_method=None).dropna()
            gmean_change = gmean(1 + changes) - 1  # geometric mean of changes
            std = changes.std()
        rows.append({
            'symbol': symbol,
            'name': get_stock_name(symbol),
            'currency': get_stock_currency(symbol),
            'weeks': len(history),
            'gmean': gmean_change,
            'std': std,
            'sharpe': (gmean_change - risk_free_return) / std,
        })

    df = pd.DataFrame(rows).sort_values(by='sharpe', ascending=False).reset_index(drop=True)
    for col in ['gmean', 'std']:
        df[col] = df[col].map(lambda x: '' if pd.isna(x) else f'{x:.2%}')
    df['sharpe'] = df['sharpe'].map(lambda x: '' if pd.isna(x) else f'{x:.2f}')
    return df


def main():
    histories = load_histories()
    # Common period: all symbols trade to the present, so the shortest
    # history sets how many recent weeks they share. Histories too short for
    # a single 52-week change are left out and get empty values.
    short_weeks = min(len(h) for h in histories.values() if len(h) > weeks)

    for name, history_weeks in [('short', short_weeks), ('3y', 156), ('5y', 261)]:
        df = crunch(histories, history_weeks)
        f = f'data/etf-picks-{name}.csv'
        df.to_csv(f, index=False)
        print(f'Saved to {f} ({history_weeks} weeks)')


if __name__ == '__main__':
    main()
