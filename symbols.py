import pandas as pd
from datetime import datetime


my_picks = [
    'SPY',
    'QQQ',
    'TOPT',
    'QTOP',
    'BRK-B', 
    'AJG',   
    'RSG',   
    # 'TQQQ',  
    # 'IGM',   
    # 'XLKS.MI', 
    # 'MGK',
    'SPMO',
    'MAGS',
    'FNGS',
    'UFO',
    'QTUM',
    'NUKZ',
    'SMH',
    'USD',
    'NVDA',
    'AVGO',
    'TSLA',
    'MSFT',
    'GOOG',
    'AAPL',
    'AMZN',
    'META',
    'CRM',
    'NFLX',
    'SHOP',
    'NET',
    'PLTR',
    'NOW',
    'SNOW',
    'WDAY',
    # 'XYZ',
    'BKNG',
    'ISRG',
    'PPA',
    'EHF1.DE', # Amundi MSCI Europe High Dividend Factor UCITS
    'ESIF.DE', # iShares MSCI Europe Financials Sector UCITS ETF
    # 'FLXD.DE', # Franklin European Quality Dividend UCITS
    # 'EXV1.DE', # iShares STOXX Europe 600 Banks UCITS ETF (DE)
    'BTC-USD',
    'GC=F' # Gold
]

etfs_with_weekly_options = [
#   'MSTY', 'MSTU', 'MSTX', 
  'EWZ', 'EEM', 'XLF', 'KWEB', 'SILJ', 'ARKK',
  'VTI', 'ASHR', 'AGQ', 'BITO', 'GDX', 'FXI', 'IVV', 'ETHA', 'IBIT',
  'SCHD', 'EFA', 'BITX', 'FEZ', 'YINN', 'FBTC', 'MAGS', 'JETS', 'XOP',
  'ARKG', 'TQQQ', 'GDXJ', 'SLV', 'QQQ', 'TNA', 'TLT', 'SQQQ', 'IEF', 'IWM',
  'NUGT', 'SOXL', 'FAS', 'ITB', 'SPY', 'XBI', 'DIA', 'UPRO', 'SVIX', 'HYG',
  'XLK', 'SPXL', 'TSLL', 'USO', 'SSO', 'VOO', 'SVXY', 'SPXU', 
  # 'NVDL', 
  'SMH',
  'IGV', 'XLY', 'TMF', 'IAU', 'GLD', 'RSP', 'KRE', 'XLV'
]

df_etfs = pd.read_csv('data/top-etfs.csv')
etfs = dict(zip(df_etfs['Symbol'], df_etfs['ETF Name']))

df_sp500 = pd.read_csv('data/sp500_stocks.csv')
sp500 = dict(zip(df_sp500['Symbol'], df_sp500['Security']))

mags_weeks = (datetime.now() - datetime(2023, 4, 8)).days // 7