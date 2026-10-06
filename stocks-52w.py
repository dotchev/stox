"""Update stocks-52w.md with the 52-week return stats of stocks-52w.ipynb,
over the weekly history common to all symbols (max 5 years).
"""
from datetime import datetime, timezone
import pandas as pd
from scipy.stats import gmean
from yfetch import get_weekly_history, get_stock_name, get_stock_currency

symbols = ['SPY', 'QQQ', 'SPMO', 'WMSE.DE', 'QTOP', 'IWDA.AS', 'SPYG',
           'AIFS.DE', 'XAIX.DE', 'XLKS.MI', 'CHIP.PA']

weeks = 52
risk_free_return = 0.04  # 4%

# Always fetch fresh data: checkout gives committed cache files a fresh mtime,
# so any cache_days > 0 would reuse stale history in CI
cache_days = 0


def load_histories():
    histories = {}
    for symbol in symbols:
        history = get_weekly_history(symbol, period='5y', cache_days=cache_days, currency='USD')
        if history.empty:
            raise RuntimeError(f'No history for {symbol}')
        histories[symbol] = history
    return histories


def crunch(histories, history_weeks):
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
        })
    return pd.DataFrame(rows).sort_values(by='sharpe', ascending=False).reset_index(drop=True)


def fmt(x, spec):
    return '' if pd.isna(x) else format(x, spec)


def main():
    histories = load_histories()
    # Common period: all symbols trade to the present, so the shortest
    # history sets how many recent weeks they share. Histories too short for
    # a single 52-week change are left out and get empty values.
    history_weeks = min((len(h) for h in histories.values() if len(h) > weeks), default=0)
    df = crunch(histories, history_weeks)
    print(df.to_string())

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    lines = [
        '# 52-Week Returns',
        '',
        f'Geometric mean and standard deviation of rolling {weeks}-week returns in USD, '
        f'over the weekly history common to all symbols (max 5 years). '
        f'Sharpe = (gmean - {risk_free_return:.0%}) / std.',
        '',
        f'Period: last {history_weeks} weeks',
        '',
        f'_Last updated: {timestamp}_',
        '',
        '| Symbol | Name | Currency | History (weeks) | Gmean | Std | Sharpe |',
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
