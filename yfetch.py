import json
import os
import random
import time
from matplotlib import ticker
import pandas as pd
import yfinance as yf
from datetime import date, datetime, timedelta
from dataclasses import dataclass


def delay():
    # Random delay to avoid hitting yfinance API rate limits
    time.sleep(random.uniform(1, 2))

history_cache_dir = os.path.join(
    os.path.dirname(__file__), 'data', 'history_cache')
os.makedirs(history_cache_dir, exist_ok=True)

metadata_cache_dir = os.path.join(
    os.path.dirname(__file__), 'data', 'metadata_cache')
os.makedirs(metadata_cache_dir, exist_ok=True)


def _metadata_file(symbol):
    return os.path.join(metadata_cache_dir, f"{symbol}.json")


def _jsonable(obj):
    """Make non-JSON-serializable metadata values (DataFrames, Timestamps)
    serializable. Called by json.dump via the `default` hook."""
    if isinstance(obj, pd.DataFrame):
        return json.loads(obj.reset_index().to_json(orient='records', date_format='iso'))
    if isinstance(obj, pd.Series):
        return json.loads(obj.to_json(date_format='iso'))
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return str(obj)


def _save_metadata(symbol, meta):
    with open(_metadata_file(symbol), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False, default=_jsonable)


def _load_metadata(symbol):
    f = _metadata_file(symbol)
    if os.path.exists(f):
        with open(f, encoding='utf-8') as fh:
            return json.load(fh)
    return None


def get_stock_metadata(symbol):
    """Get the full history metadata for a symbol, cached permanently as
    data/metadata_cache/<symbol>.json.

    Reuses metadata captured during get_stock_history (no extra request).
    Only on a true miss does it make a single lightweight chart request.
    """
    meta = _load_metadata(symbol)
    if meta is not None:
        return meta

    delay()
    meta = yf.Ticker(symbol).get_history_metadata()
    _save_metadata(symbol, meta)
    return _load_metadata(symbol)  # round-trip so callers get plain JSON types


def get_stock_name(symbol):
    """Get the stock/ETF display name from the cached metadata."""
    meta = get_stock_metadata(symbol)
    return meta.get('longName') or meta.get('shortName') or symbol


_interval_units = {
    'm': 'minutes',
    'h': 'hours',
    'd': 'days',
    'wk': 'weeks',
    'mo': 'months',
}


def _interval_unit(interval):
    """Name the time unit of an interval (e.g. '1d' -> 'days')."""
    return _interval_units.get(interval.lstrip('0123456789'), 'rows')


def get_stock_history(symbol, period='5y', interval='1d', cache_days=2):
    """Get stock history with caching

    Args:
        symbol (str): Stock symbol
        period (str): Period to fetch data for (e.g. '5y', '1mo')
        interval (str): Interval for data points (e.g. '1d', '1h')
        cache_days (int): Number of days to consider cached data as fresh

    Returns:
        pandas.DataFrame: Historical stock data
    """
    cache_file = os.path.join(
        history_cache_dir, f"{symbol}_{period}_{interval}.csv")

    # Check if cache exists and is recent enough
    if os.path.exists(cache_file):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_mod_time < timedelta(days=cache_days):
            history = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            history.index = pd.to_datetime(history.index, utc=True)
            # print(f"Loaded cached history for {symbol} ({len(history)} rows)")
            if not history.empty:  # an empty cache file is a stale failed fetch
                return history

    # Fetch fresh data
    delay()
    ticker_data = yf.Ticker(symbol)
    history = ticker_data.history(interval=interval, period=period)
    print(f"Fetched history for {symbol} ({len(history)} {_interval_unit(interval)})")

    # Capture the full metadata from the same request (no extra API call)
    try:
        _save_metadata(symbol, ticker_data.get_history_metadata())
    except Exception:
        pass

    # Cache the result, but never an empty fetch: Yahoo returns no rows on
    # transient failures, and caching that would hide good data for cache_days.
    if history.empty:
        print(f"No history for {symbol}, not caching")
    else:
        history.to_csv(cache_file)

    return history


_weekly_agg = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum',
    'Dividends': 'sum',
    'Stock Splits': 'sum',
    'Capital Gains': 'sum',
}


def to_weekly(daily, symbol=None):
    """Aggregate daily bars into Monday-anchored weekly bars, matching Yahoo's
    1wk data.

    Weeks are binned in the exchange timezone (taken from the cached metadata
    when a symbol is given), so that a Monday bar of a non-US exchange does not
    fall into the previous week.

    Args:
        daily (pandas.DataFrame): Daily history, as returned by get_stock_history
        symbol (str): Symbol the history belongs to, to look up its exchange timezone

    Returns:
        pandas.DataFrame: Weekly history, indexed by the Monday of each week
    """
    if daily.empty:
        return daily

    index_tz = daily.index.tz
    exchange_tz = get_stock_metadata(symbol).get(
        'exchangeTimezoneName') if symbol else None
    if exchange_tz and index_tz is not None:
        daily = daily.tz_convert(exchange_tz)

    agg = {c: a for c, a in _weekly_agg.items() if c in daily.columns}
    weekly = daily.resample('W-MON', label='left', closed='left').agg(agg)
    weekly = weekly.dropna(subset=['Open'])  # weeks without trading days

    if exchange_tz and index_tz is not None:
        weekly = weekly.tz_convert(index_tz)
    return weekly


def get_weekly_history(symbol, period='5y', cache_days=2):
    """Get weekly stock history, derived from the daily history rather than
    fetched separately - see get_stock_history and to_weekly."""
    daily = get_stock_history(symbol, period=period,
                              interval='1d', cache_days=cache_days)
    return to_weekly(daily, symbol)


option_chains_dir = os.path.join(
    os.path.dirname(__file__), 'data', 'option_chains')
os.makedirs(option_chains_dir, exist_ok=True)


@dataclass
class OptionChain:
    calls: pd.DataFrame
    puts: pd.DataFrame

    def validate(self, stock_price: float, symbol: str, expiration: str):
        itm = self.calls[self.calls['inTheMoney'] == True]
        assert not itm.empty, f'No ITM calls for {symbol} on {expiration}'
        otm = self.calls[self.calls['inTheMoney'] == False]
        assert not otm.empty, f'No OTM calls for {symbol} on {expiration}'
        assert itm.iloc[-1].strike <= stock_price <= otm.iloc[0].strike, \
            f'Stock price {stock_price} for {symbol} is not between ITM and OTM strikes on {expiration}'

    def get_calls(self) -> list[tuple[float, float]]:
        """Return a list of all calls as (strike_price, mid_price) tuples."""
        result = []
        for _, row in self.calls.iterrows():
            strike_price = row['strike']
            mid_price = (row['bid'] + row['ask']) / 2
            result.append((strike_price, mid_price))
        return result

    def get_puts(self) -> list[tuple[float, float]]:
        """Return a list of all puts as (strike_price, mid_price) tuples."""
        result = []
        for _, row in self.puts.iterrows():
            strike_price = row['strike']
            mid_price = (row['bid'] + row['ask']) / 2
            result.append((strike_price, mid_price))
        return result

    def get_itm_calls(self) -> list[tuple[float, float]]:
        """Return a list of ITM calls as (strike_price, mid_price) tuples."""
        itm_calls = self.calls[self.calls['inTheMoney'] == True]
        result = []
        for _, row in itm_calls.iterrows():
            strike_price = row['strike']
            mid_price = (row['bid'] + row['ask']) / 2
            result.append((strike_price, mid_price))
        return result

    def get_otm_calls(self) -> list[tuple[float, float]]:
        """Return a list of OTM calls as (strike_price, mid_price) tuples."""
        otm_calls = self.calls[self.calls['inTheMoney'] == False]
        result = []
        for _, row in otm_calls.iterrows():
            strike_price = row['strike']
            mid_price = (row['bid'] + row['ask']) / 2
            result.append((strike_price, mid_price))
        return result

@dataclass
class OptionChains:
    symbol: str
    info: dict
    market_date: date
    stock_price: float
    chains: dict[str, OptionChain]  # expiration : OptionChain


def get_option_chains(symbol: str, as_of: str = None, expiry: str = None) -> OptionChains:
    ticker = yf.Ticker(symbol)
    if as_of is None:
        info = ticker.info
        market_date = datetime.fromtimestamp(info['regularMarketTime']).date()
        date_dir = os.path.join(option_chains_dir, symbol, market_date.isoformat())
        os.makedirs(date_dir, exist_ok=True)

        info_file = os.path.join(date_dir, 'info.json')
        with open(info_file, 'w') as f:
            json.dump(info, f, indent=2, default=str)
    else:
        market_date = date.fromisoformat(as_of)
        date_dir = os.path.join(option_chains_dir, symbol, market_date.isoformat())
        info = json.load(open(os.path.join(date_dir, 'info.json')))

    result = OptionChains(
        symbol=symbol,
        info=info,
        market_date=market_date,
        stock_price=info['regularMarketPrice'],
        chains={}
    )

    def fetch_chain(expiry: str) -> OptionChain:
        exp_dir = os.path.join(date_dir, expiry)
        os.makedirs(exp_dir, exist_ok=True)

        calls_file = os.path.join(exp_dir, 'calls.csv')
        puts_file = os.path.join(exp_dir, 'puts.csv')

        if os.path.exists(calls_file) and os.path.exists(puts_file):
            calls = pd.read_csv(calls_file, index_col=0, parse_dates=["lastTradeDate"])
            puts = pd.read_csv(puts_file, index_col=0, parse_dates=["lastTradeDate"])
            option_chain = OptionChain(calls=calls, puts=puts)
        else:
            print(f"Fetching option chain for {symbol} expiring on {expiry}")
            delay()
            chain = ticker.option_chain(expiry)
            chain.calls.to_csv(calls_file)
            chain.puts.to_csv(puts_file)
            option_chain = OptionChain(calls=chain.calls, puts=chain.puts)

        option_chain.validate(result.stock_price, symbol, expiry)
        return option_chain

    if expiry is None:
        # Fetch all expiration dates
        expiration_dates = ticker.options
        for expiry in expiration_dates:
            result.chains[expiry] = fetch_chain(expiry)
    else:
        # Fetch specific expiration date
        result.chains[expiry] = fetch_chain(expiry)

    return result
