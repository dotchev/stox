"""Update stocks-52w.md with the 52-week return stats of stocks-52w.ipynb,
over the weekly history common to all symbols (max 5 years).
"""
from datetime import datetime, timezone
import pandas as pd
from scipy.stats import gmean
from yfetch import get_weekly_history, get_stock_name, get_stock_currency, get_stock_metadata

symbols = ['SPY', 'QQQ', 'SPMO', 'WMSE.DE', 'QTOP', 'IWDA.AS', 'SPYG']

weeks = 52
risk_free_return = 0.04  # 4%

# Always fetch fresh data: checkout gives committed cache files a fresh mtime,
# so any cache_days > 0 would reuse stale history in CI
cache_days = 0


def week_dates(history, symbol):
    """Monday dates of weekly bars in the exchange timezone, comparable across
    exchanges."""
    index = history.index
    tz = get_stock_metadata(symbol).get('exchangeTimezoneName')
    if tz and index.tz is not None:
        index = index.tz_convert(tz)
    index = index.normalize()
    return index.tz_localize(None) if index.tz is not None else index


def load_histories():
    histories = {}
    for symbol in symbols:
        history = get_weekly_history(symbol, period='5y', cache_days=cache_days, currency='USD')
        if history.empty:
            raise RuntimeError(f'No history for {symbol}')
        history.index = week_dates(history, symbol)
        histories[symbol] = history
    return histories


def crunch(histories, start, end):
    rows = []
    for symbol, history in histories.items():
        history = history[(history.index >= start) & (history.index <= end)]
        changes = history.Close.pct_change(periods=weeks, fill_method=None).dropna()
        gmean_change = gmean(1 + changes) - 1 if len(changes) else float('nan')
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
    return pd.DataFrame(rows).sort_values(by='sharpe', ascending=False).reset_index(drop=True)


def fmt(x, spec):
    return '' if pd.isna(x) else format(x, spec)


def main():
    histories = load_histories()
    # Common period: the weeks covered by all symbols
    start = max(h.index[0] for h in histories.values())
    end = min(h.index[-1] for h in histories.values())
    df = crunch(histories, start, end)
    print(df.to_string())

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    period_weeks = df['weeks'].max()

    lines = [
        '# 52-Week Returns',
        '',
        f'Geometric mean and standard deviation of rolling {weeks}-week returns in USD, '
        f'over the weekly history common to all symbols (max 5 years). '
        f'Sharpe = (gmean - {risk_free_return:.0%}) / std.',
        '',
        f'Period: weeks of {start:%Y-%m-%d} to {end:%Y-%m-%d} ({period_weeks} weeks)',
        '',
        f'_Last updated: {timestamp}_',
        '',
        '| Symbol | Name | Currency | Weeks | Gmean | Std | Sharpe |',
        '|---|---|---|---|---|---|---|',
    ]
    for r in df.itertuples():
        lines.append(f'| {r.symbol} | {r.name} | {r.currency} | {r.weeks} | '
                     f'{fmt(r.gmean, ".2%")} | {fmt(r.std, ".2%")} | {fmt(r.sharpe, ".2f")} |')

    with open('stocks-52w.md', 'w') as f:
        f.write('\n'.join(lines) + '\n')

    print('Wrote stocks-52w.md')


if __name__ == '__main__':
    main()
