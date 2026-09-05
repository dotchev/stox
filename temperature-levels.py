"""Update temperature-levels.md with P25/P75 price levels based on the
% distance of Close from the 200-day SMA, over the last 5 years.
"""
from datetime import datetime, timezone
from yfetch import get_stock_history, get_stock_metadata

symbols = ['SPMO', 'SPYG', 'SMH', 'USD', 'TDIV.AS', 'ESIF.DE', '4GLD.DE', 'JEDI.DE']

currency_symbols = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
}


def compute_levels(symbol):
    history = get_stock_history(symbol, period='5y', interval='1d')
    currency = get_stock_metadata(symbol).get('currency', '')
    sma200 = history['Close'].rolling(window=200).mean()
    dist = (history['Close'] / sma200 - 1).dropna()
    price = history['Close'].iloc[-1]
    current_sma = sma200.iloc[-1]
    current_dist = dist.iloc[-1]
    percentile = (dist < current_dist).mean()
    p25 = current_sma * (1 + dist.quantile(0.25))
    p75 = current_sma * (1 + dist.quantile(0.75))
    return currency, price, percentile, p25, p75


def format_percentile(percentile):
    text = f'{percentile:.0%}'
    if percentile > 0.75 or percentile < 0.25:
        return f'**{text}**'
    return text


def main():
    rows = []
    for symbol in symbols:
        currency, price, percentile, p25, p75 = compute_levels(symbol)
        rows.append((symbol, currency, price, percentile, p25, p75))
        print(f'{symbol}: Price={price:.2f} {currency} P={percentile:.0%} P25={p25:.2f} P75={p75:.2f}')

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    lines = [
        '# Temperature Levels',
        '',
        'Price levels corresponding to the P25 and P75 of the % distance of '
        'Close from the 200-day SMA, over the last 5 years.',
        '',
        f'_Last updated: {timestamp}_',
        '',
        '| Symbol | Price | P | P25 | P75 |',
        '|---|---|---|---|---|',
    ]
    for symbol, currency, price, percentile, p25, p75 in rows:
        cur = currency_symbols.get(currency, currency + ' ')
        lines.append(f'| {symbol} | {cur}{price:,.2f} | {format_percentile(percentile)} | {cur}{p25:,.2f} | {cur}{p75:,.2f} |')

    with open('temperature-levels.md', 'w') as f:
        f.write('\n'.join(lines) + '\n')

    print('Wrote temperature-levels.md')


if __name__ == '__main__':
    main()
