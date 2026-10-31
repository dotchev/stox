"""Write data/folio.csv with per-symbol return, risk, range, revenue growth
and T200 stats for the portfolio watchlist.
"""
import json
import os
import pandas as pd
import yfinance as yf
from datetime import date
from scipy.stats import gmean
from yfetch import delay, get_stock_history, get_stock_name, get_stock_metadata, to_weekly

risk_free_return = 4/100
history_weeks = 3 * 52 # 3Y
change_weeks = 52 # 1Y
range_window = 4 # ~ month
cache_days = 5 # how long to cache stock data
revenue_cache_file = 'data/revenue_cache.json'

symbols = [
    'MAGS', # Roundhill Magnificent Seven ETF
    'QTOP.AS', # iShares VII PLC - iShares Nasdaq 100 Top 30 UCITS ETF USD (Acc)
    'FNGS', # MicroSectors FANG+ ETN
    'IGM', # iShares Expanded Tech Sector ETF
    'SPYG', # State Street SPDR Portfolio S&P 500 Growth ETF
    'SPMO', # Invesco S&P 500 Momentum ETF
    'WMSE.DE', # Amundi MSCI World Momentum Screened Factor UCITS ETF USD Acc
    'IWMO.MI', # iShares Edge MSCI World Momentum Factor UCITS ETF USD (Acc)
    'TSLA', # Tesla, Inc.
    'NVDA', # NVIDIA Corporation
    'AVGO', # Broadcom Inc.
    'SMH', # VanEck Semiconductor ETF
    'CHIP.PA', # Amundi MSCI Semiconductors UCITS ETF Acc
    'USD', # ProShares Ultra Semiconductors
    'TDIV.AS', # VanEck Morningstar Developed Markets Dividend Leaders UCITS ETF
    'ESIF.DE', # iShares MSCI Europe Financials Sector UCITS ETF
    'DFEN.DE', # VanEck Defense ETF A USD Acc
    'ASWC.DE', # HANetf ICAV - Future of Defence UCITS ETF - Accumulating
    'XWEM.DE', # Xtrackers MSCI World Momentum ESG UCITS ETF 1C
    'VHVE.MI', # Vanguard FTSE Developed World UCITS ETF USD Accumulation
    'EXI', # iShares Global Industrials ETF
    '4GLD.DE', # Xetra-Gold
    'BRK-B', # Berkshire Hathaway Inc.
    'NFLX', # Netflix, Inc.
    'PLTR', # Palantir Technologies Inc.
    'NET', # Cloudflare, Inc.
    'ISRG', # Intuitive Surgical, Inc.
    'SHOP', # Shopify Inc.
    'DAPP', # VanEck Digital Transformation ETF
    'DAPP.MI', # VanEck Crypto& Blockchain Innovators ETF A USD Acc
    'BITQ', # Bitwise Crypto Industry Innovators ETF
    'UFO', # Procure Space ETF
    'ROKT', # State Street SPDR S&P Kensho Final Frontiers ETF
    'JEDI.DE', # VanEck Space Innovators UCITS ETF A USD Acc
    'WSPC.PA', # WisdomTree Space Economy UCITS ETF USD Acc
    'SPCX', # Space Exploration Technologies Corp.
    'RKLB', # Rocket Lab Corporation
    'PL', # Planet Labs PBC
    'NASA', # Tema Space Innovators ETF
    'NUKZ', # Range Nuclear Renaissance ETF
    'NLR', # VanEck Uranium and Nuclear ETF
    'NUKL.DE', # VanEck Uranium and Nuclear Technologies UCITS ETF A USD Acc
    'AIPO', # Defiance AI & Power Infrastructure ETF
    'A1P0.DE', # Defiance AI & Power Infrastructure ETF USD Acc
    'XAIX.DE', # Xtrackers Artificial Intelligence & Big Data UCITS ETF 1C
    'AIFS.DE', # iShares AI Infrastructure UCITS ETF USD (Acc)
    '5MVL.DE', # iShares Edge MSCI EM Value Factor UCITS ETF USD (Acc)
    'QTUM', # Defiance Quantum ETF
    'WQTM.PA', # WisdomTree Quantum Computing UCITS ETF - USD Acc
    'AGIX', # KraneShares Artificial Intelligence and Technology Public and Private ETF
    'CHAT', # Roundhill Generative AI & Technology ETF
    'BAI', # iShares A.I. Innovation and Tech Active ETF
    'ARKG', # ARK Genomic Revolution ETF
    'AAKG.DE', # ARK Genomic Revolution UCITS ETF Class A USD Accumulation
    'PPA', # Invesco Aerospace & Defense ETF
    'IVDF.DE', # Invesco Markets II plc - Invesco Defence Innovation UCITS ETF
    'QQQ', # Invesco QQQ Trust
    'COIN', # Coinbase Global, Inc.
    'NKE', # NIKE, Inc.
    'STLA', # Stellantis N.V.
    'AMAT', # Applied Materials, Inc.
]

try:
    with open(revenue_cache_file) as f:
        revenue_cache = json.load(f)
except FileNotFoundError:
    revenue_cache = {}

def fetch_revenue_growth(symbol):
    """(year over year growth of the latest quarterly revenue, quarter end date),
    (None, None) if unavailable."""
    delay()
    qis = yf.Ticker(symbol).quarterly_income_stmt
    if 'Total Revenue' not in qis.index:
        print(f'No revenue for {symbol}')
        return None, None
    rev = qis.loc['Total Revenue'].dropna().sort_index(ascending=False)
    if len(rev) < 5:
        print(f'Not enough revenue history for {symbol}: {len(rev)} quarters, need 5')
        return None, None
    return round(float(rev.iloc[0] / rev.iloc[4] - 1), 4), str(rev.index[0].date())

def format_revenue(growth, quarter):
    return 'n/a' if growth is None else f'{growth:.2%} ({quarter})'

def get_revenue_growth(symbol):
    """Revenue growth from data/revenue_cache.json, refetched once it goes stale."""
    if get_stock_metadata(symbol).get('instrumentType') != 'EQUITY':
        return None # ETFs and the like have no revenue

    today = date.today()
    cached = revenue_cache.get(symbol)
    if cached and (today - date.fromisoformat(cached['fetched'])).days < cache_days:
        return cached['growth']

    growth, quarter = fetch_revenue_growth(symbol)
    if cached and (growth, quarter) != (cached['growth'], cached['quarter']):
        print(f'{symbol} revenue: {format_revenue(cached["growth"], cached["quarter"])}'
              f' => {format_revenue(growth, quarter)}')

    revenue_cache[symbol] = {'growth': growth, 'quarter': quarter, 'fetched': today.isoformat()}
    os.makedirs(os.path.dirname(revenue_cache_file), exist_ok=True)
    with open(revenue_cache_file, 'w') as f:
        json.dump(revenue_cache, f, indent=2, sort_keys=True)
    return growth

def temperature(series):
    """Share of past values at or below the last one, None if the series is empty."""
    series = series.dropna()
    if len(series) == 0:
        return None
    return (series <= series.iloc[-1]).mean()

def sma_temperature(symbol, daily, window=200):
    """Temperature of the distance to the SMA over daily history."""
    sma = daily.Close.rolling(window=window).mean()
    if sma.dropna().empty:
        print(f'Not enough history for {symbol}: {len(daily)} days, need {window}')
        return None
    return temperature(daily.Close / sma - 1)


def main():
    rows = []
    for symbol in symbols:
        # one daily fetch per symbol - the weekly bars are aggregated from it
        daily = get_stock_history(symbol, period='5y', interval='1d', cache_days=cache_days)
        weekly = to_weekly(daily, symbol).tail(history_weeks)

        if len(weekly) < history_weeks:
            print(f'Not enough history for {symbol}: {len(weekly)} weeks, need {history_weeks}')
            gmean_change = std = sharpe = None
        else:
            changes = weekly.Close.pct_change(periods=change_weeks, fill_method=None).dropna()
            gmean_change = gmean(1 + changes) - 1 # geometric mean of changes
            std = changes.std()
            sharpe = (gmean_change - risk_free_return) / std

        high = weekly.High.rolling(range_window).max()
        low = weekly.Low.rolling(range_window).min()
        range = ((high - low) / (high + low) * 2).dropna() # relative range per window

        rows.append({
            'symbol': symbol, # ticker as given to yfinance
            'name': get_stock_name(symbol), # short name from yfinance metadata
            'price': weekly.Close.iloc[-1], # last close
            'weeks': len(weekly), # weekly bars used, capped at history_weeks (3Y = 156)
            'gmean': gmean_change, # geometric mean of the 52w changes over 3y
            'std': std, # std dev of the same 52w changes over 3y
            'sharpe': sharpe, # (gmean - risk_free_return 4%) / std
            'range': range.mean(), # mean of 2*(high-low)/(high+low) over rolling range_window (4W)
            'revenue': get_revenue_growth(symbol), # YoY growth of latest quarterly revenue
            'T200': sma_temperature(symbol, daily, window=200), # T200 over 5y
        })

    df = pd.DataFrame(rows)
    f = f'data/folio.csv'
    df.to_csv(f, index=False)
    print(f'Saved to {f} ({len(df)} rows)')

    df = df.reset_index(drop=True)
    for col in ['gmean', 'std', 'range', 'revenue', 'T200']:
        df[col] = df[col].map(lambda v: None if pd.isna(v) else f'{v:.2%}')
    print(df.to_string())


if __name__ == '__main__':
    main()
