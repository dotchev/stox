"""Update temperature-levels.md with P25/P75 price levels based on the
% distance of Close from the 200-day SMA, over the last 5 years.
"""
from datetime import datetime, timezone
from yfetch import get_stock_history

symbols = ['SPMO', 'SPYG', 'SMH', 'USD']


def compute_levels(symbol):
    history = get_stock_history(symbol, period='5y', interval='1d')
    sma200 = history['Close'].rolling(window=200).mean()
    dist = (history['Close'] / sma200 - 1).dropna()
    current_sma = sma200.iloc[-1]
    p25 = current_sma * (1 + dist.quantile(0.25))
    p75 = current_sma * (1 + dist.quantile(0.75))
    return p25, p75


def main():
    rows = []
    for symbol in symbols:
        p25, p75 = compute_levels(symbol)
        rows.append((symbol, p25, p75))
        print(f'{symbol}: P25={p25:.2f} P75={p75:.2f}')

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    lines = [
        '# Temperature Levels',
        '',
        'Price levels corresponding to the P25 and P75 of the % distance of '
        'Close from the 200-day SMA, over the last 5 years.',
        '',
        f'_Last updated: {timestamp}_',
        '',
        '| Symbol | P25 | P75 |',
        '|---|---|---|',
    ]
    for symbol, p25, p75 in rows:
        lines.append(f'| {symbol} | {p25:.2f} | {p75:.2f} |')

    with open('temperature-levels.md', 'w') as f:
        f.write('\n'.join(lines) + '\n')

    print('Wrote temperature-levels.md')


if __name__ == '__main__':
    main()
