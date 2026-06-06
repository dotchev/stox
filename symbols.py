import pandas as pd
from datetime import datetime


my_stocks = [
    'BRK-B', 
    # 'AJG',   
    # 'RSG',   
    # 'AZO',
    'PL',
    'RKLB',
    'NVDA',
    'AVGO',
    'TSLA',
    'MSFT',
    'GOOG',
    'AAPL',
    'AMZN',
    'META',
    # 'CRM',
    'NFLX',
    'SHOP',
    'NET',
    'PLTR',
    # 'NOW',
    # 'SNOW',
    # 'WDAY',
    # 'XYZ',
    'BKNG',
    'ISRG',
]

my_etfs = [
    'SPY',
    # 'SPYG',
    # 'SPYV',
    'QQQ',
    # 'TOPT',
    # 'QTOP',
    # 'TQQQ',  
    'IGM',   
    # 'XLKS.MI', 
    # 'MGK',
    'SPMO',
    'MAGS',
    'FNGS',
    'UFO',
    'ROKT',
    # 'ARKX',
    'QTUM',
    'NUKZ',
    'SMH',
    'USD',
    'PPA',
    'DAPP',
    'BITQ',
    # 'LVHI',    # Franklin International Low Volatility High Dividend Index ETF
    'EHF1.DE', # Amundi MSCI Europe High Dividend Factor UCITS
    'ESIF.DE', # iShares MSCI Europe Financials Sector UCITS ETF
    'VDIV.DE', # VanEck Morningstar Developed Markets Dividend Leaders UCITS ETF
    'JEDI.DE', # VanEck Space Innovators UCITS ETF
    'XLKS.MI', # Invesco Technology S&P US Select Sector UCITS ETF
    'SMH.MI',  # VanEck Vectors Semiconductor UCITS ETF
    'CHIP.PA', # Amundi MSCI Semiconductors UCITS ETF Acc
    'DFEN.DE', # VanEck Defense ETF A USD Acc
    'BTC-USD',
    'GC=F' # Gold
]

my_picks = my_stocks + my_etfs

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