import os
import json
import pandas as pd
import yfinance as yf
import time

stocks_history_dir = 'data/stock_history'
os.makedirs(stocks_history_dir, exist_ok=True)

# with open('data/finhub-us-symbols.json', 'r') as file:
#   symbols = json.load(file)
# symbols = [s for s in symbols if s['currency'] == 'USD' and s['type'] in ('ETP') and s['mic'] != 'OOTC']

# symbols = pd.read_csv('data/sp500_stocks.csv')

etf_data = pd.read_csv('data/top-etfs.csv')
symbols = [{"symbol": symbol, "description": symbol} for symbol in etf_data['Symbol'].tolist()]
print(f'Loaded {len(symbols)} symbols')

for i, s in enumerate(symbols):
  symbol = s["symbol"].replace('.', '-') # for yahoo finance compatibility
  description = s["description"]

  f = stocks_history_dir + '/' + symbol + '.csv'
  if os.path.exists(f):
      continue
  
  print(f'Processing {i+1}/{len(symbols)} - {symbol} ({description})')
  try:
      td = yf.Ticker(symbol)
      history = td.history(interval='1wk', period='5y')
  except Exception as e:
      print(f"Failed to fetch history for {symbol}: {e}")
      continue

  print(f'Fetched {len(history)} weeks of history')
  history.to_csv(f)

  time.sleep(1)  # avoid rate limits