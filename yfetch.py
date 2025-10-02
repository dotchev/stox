import json
import os
import time
from time import sleep
from matplotlib import ticker
import pandas as pd
import yfinance as yf
from datetime import date, datetime, timedelta
from dataclasses import dataclass

history_cache_dir = os.path.join(
    os.path.dirname(__file__), 'data', 'history_cache')
os.makedirs(history_cache_dir, exist_ok=True)


def get_stock_history(symbol, period='5y', interval='1d', cache_days=6):
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
            # print(f"Loaded cached history for {symbol} ({len(history)} rows)")
            return history

    # Fetch fresh data
    sleep(1)  # Sleep to avoid hitting API rate limits
    ticker_data = yf.Ticker(symbol)
    history = ticker_data.history(interval=interval, period=period)
    print(f"Fetched history for {symbol} ({len(history)} rows)")

    # Cache the result
    history.to_csv(cache_file)

    return history


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
            sleep(1)  # Sleep to avoid hitting API rate limits
            start_time = time.perf_counter()
            chain = ticker.option_chain(expiry)
            elapsed = time.perf_counter() - start_time
            print(f"ticker.option_chain({expiry}) took {elapsed:.3f} seconds")
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
