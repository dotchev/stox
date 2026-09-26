import pandas as pd
from datetime import datetime


my_stocks = [
    'BRK-B', 
    # 'AJG',   
    # 'RSG',   
    # 'AZO',
    # 'PL',
    # 'RKLB',
    'NVDA',
    'AVGO',
    'TSLA',
    # 'MSFT',
    # 'GOOG',
    # 'AAPL',
    # 'AMZN',
    # 'META',
    # 'CRM',
    # 'NFLX',
    # 'SHOP',
    # 'NET',
    # 'PLTR',
    # 'NOW',
    # 'SNOW',
    # 'WDAY',
    # 'XYZ',
    # 'BKNG',
    # 'ISRG',
]

my_etfs = [
    'SPY',
    'SPYG',
    'SPYV',
    'QQQ',
    'TOPT',
    'QTOP',
    'QTOP.AS',
    'TQQQ',  
    'IGM',   
    'MGK',
    'SPMO',
    'IDMO',
    'MAGS',
    'FNGS',
    'EXI',
    'UFO',
    'ROKT',
    'QTUM',
    'WQTM.DE', # WisdomTree Quantum Computing UCITS ETF - USD Acc
    'NUKZ',
    'SMH',
    'USD',
    'PPA',
    'IVDF.DE',
    'DAPP',
    'BITQ',
    'FBT.MI', # First Trust NYSE Arca Biotechnology UCITS ETF Class A USD Accumulation
    'A1P0.DE', # Defiance AI & Power Infrastructure ETF USD Acc
    'LVHI',    # Franklin International Low Volatility High Dividend Index ETF
    'EHF1.DE', # Amundi MSCI Europe High Dividend Factor UCITS
    'ESIF.DE', # iShares MSCI Europe Financials Sector UCITS ETF
    'EXV1.DE', # iShares STOXX Europe 600 Banks UCITS ETF (DE)
    'VDIV.DE', # VanEck Morningstar Developed Markets Dividend Leaders UCITS ETF
    'JEDI.DE', # VanEck Space Innovators UCITS ETF
    'XLKS.MI', # Invesco Technology S&P US Select Sector UCITS ETF
    'XAIX.DE', # Xtrackers Artificial Intelligence & Big Data UCITS ETF 1C
    'SMH.MI',  # VanEck Vectors Semiconductor UCITS ETF
    'CHIP.PA', # Amundi MSCI Semiconductors UCITS ETF Acc
    'DFEN.DE', # VanEck Defense ETF A USD Acc
    'ASWC.DE', # HANetf ICAV - Future of Defence UCITS ETF - Accumulating
    'EUNL.DE', # iShares Core MSCI World UCITS ETF USD (Acc)
    'IS3S.DE', # iShares Edge MSCI World Value Factor UCITS ETF
    'IWMO.MI', # iShares Edge MSCI World Momentum Factor UCITS ETF
    '5MVL.DE', # iShares Edge MSCI EM Value Factor UCITS ETF USD (Acc)
    'WMSE.DE', # Amundi MSCI World Momentum Advanced UCITS ETF Acc
    'XWEM.DE', # Xtrackers MSCI World Momentum ESG UCITS ETF 1C
    'XDWI.DE', # Xtrackers MSCI World Industrials UCITS ETF 1C
    '4GLD.DE', # Xetra-Gold
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