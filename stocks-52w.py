"""Update stocks-52w.md with the 52-week return stats of stocks-52w.ipynb,
over the weekly history common to all symbols (max 5 years).
"""
from datetime import datetime, timezone
from textwrap import dedent
import pandas as pd
from scipy.stats import gmean
from yfetch import (get_stock_history, get_stock_name, get_stock_currency,
                    to_currency, to_weekly)

symbols = [
    'SPY',      # State Street SPDR S&P 500 ETF Trust
    'QQQ',      # Invesco QQQ Trust
    'TOPT',     # iShares Top 20 U.S. Stocks ETF
    'MAGS',     # Roundhill Magnificent Seven ETF
    'QTOP',     # iShares Nasdaq Top 30 Stocks ETF
    'WMSE.DE',  # Amundi MSCI World Momentum Screened Factor UCITS ETF USD Acc
    'VHVE.MI',  # Vanguard FTSE Developed World UCITS ETF USD Accumulation
    'AIFS.DE',  # iShares AI Infrastructure UCITS ETF USD (Acc)
    'XAIX.DE',  # Xtrackers Artificial Intelligence & Big Data UCITS ETF 1C
    'XLKS.MI',  # Invesco Technology S&P US Select Sector UCITS ETF
    'CHIP.PA',  # Amundi MSCI Semiconductors UCITS ETF Acc
    'XWEM.DE',  # Xtrackers MSCI World Momentum ESG UCITS ETF 1C
    'VDIV.DE',  # VanEck Morningstar Developed Markets Dividend Leaders UCITS ETF
]

weeks = 52
risk_free_return = 0.04  # 4%
sma_window = 200  # days

# Reuse history fetched within the last day
cache_days = 1


def sma_temperature(closes, window=sma_window):
    """Share of past distances to the SMA below the current one; NaN when there
    is less than `window` days of history."""
    dist = (closes / closes.rolling(window=window).mean() - 1).dropna()
    if dist.empty:
        return float('nan')
    return (dist < dist.iloc[-1]).mean()


def load_histories():
    """Weekly USD histories for the returns, and T200 per symbol from the
    native-currency daily closes, both from one fetch of the daily history."""
    histories, t200 = {}, {}
    for symbol in symbols:
        daily = get_stock_history(symbol, period='5y', interval='1d', cache_days=cache_days)
        if daily.empty:
            raise RuntimeError(f'No history for {symbol}')
        # Yahoo sometimes returns a last row with volume but no prices
        t200[symbol] = sma_temperature(daily.Close.dropna())
        usd = to_currency(daily, symbol, 'USD', period='5y', cache_days=cache_days)
        histories[symbol] = to_weekly(usd, symbol)
    return histories, t200


def crunch(histories, t200, history_weeks):
    rows = []
    for symbol, history in histories.items():
        available_weeks = len(history)
        history = history.tail(history_weeks)
        changes = history.Close.pct_change(periods=weeks, fill_method=None).dropna()
        gmean_change = gmean(1 + changes) - 1 if len(changes) else float('nan')
        std = changes.std()
        rows.append({
            'symbol': symbol,
            'name': get_stock_name(symbol),
            'currency': get_stock_currency(symbol),
            'weeks': available_weeks,
            'gmean': gmean_change,
            'std': std,
            'sharpe': (gmean_change - risk_free_return) / std,
            't200': t200[symbol],
        })
    return pd.DataFrame(rows).sort_values(by='sharpe', ascending=False).reset_index(drop=True)


def fmt(x, spec):
    return '' if pd.isna(x) else format(x, spec)


def fmt_t200(t200):
    text = fmt(t200, '.0%')
    if text and (t200 > 0.9 or t200 < 0.1):
        return f'**{text}**'
    return text


def main():
    histories, t200 = load_histories()
    # Common period: all symbols trade to the present, so the shortest
    # history sets how many recent weeks they share. Histories too short for
    # a single 52-week change are left out and get empty values.
    lengths = {s: len(h) for s, h in histories.items() if len(h) > weeks}
    limiting_symbol = min(lengths, key=lengths.get, default=None)
    history_weeks = lengths.get(limiting_symbol, 0)
    df = crunch(histories, t200, history_weeks)
    print(df.to_string())

    with open('stocks-52w.md', 'w') as f:
        f.write(dedent(f"""\
            # 52-Week Returns

            Geometric mean and standard deviation of rolling {weeks}-week returns in USD,
            over the weekly history common to all symbols (max 5 years).

            Sharpe = (gmean - {risk_free_return:.0%}) / std.

            T200 = percentile of the current distance from the {sma_window}-day SMA
            within its 5-year history. Empty if history < {sma_window} days.

            Return Period: last {history_weeks} weeks (limited by {limiting_symbol})

            _Last updated: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}_

            | Symbol | Name | Currency | History (weeks) | Gmean | Std | Sharpe | T200 |
            |---|---|---|---|---|---|---|---|
            """))
        
        for r in df.itertuples():
            f.write(f'| {r.symbol} | {r.name} | {r.currency} | {r.weeks} | '
                    f'{fmt(r.gmean, ".2%")} | {fmt(r.std, ".2%")} | {fmt(r.sharpe, ".2f")} | '
                    f'{fmt_t200(r.t200)} |\n')
            
        f.write('\nGenerated by [stocks-52w.py](stocks-52w.py).\n')

    print('Wrote stocks-52w.md')


if __name__ == '__main__':
    main()
