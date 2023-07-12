from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.helpers import date_to_milliseconds
import pandas as pd
import talib
import numpy as np
from datetime import datetime, timedelta

# Binance API keys, obtained from your account on Binance
api_key = '2jGIc7G272Jy8VD5DG94ro7AD5SRKTTcHBzgRoUZQOWm1kMVOPyLKWQfxuVfS1jv'
api_secret = 'WVAk3mnz2uhRSvgr8Kt06ACzhiTyGKGJjniRRwrZMJ477CYS5ADfGat4ze791Ek7'

def scalping_bot(symbol, interval, limit, fast_ma, slow_ma):
    client = Client(api_key, api_secret)
    klines = client.get_historical_klines(symbol, interval, limit + " day ago UTC")
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

    data['close'] = pd.to_numeric(data['close'])
    data['high'] = pd.to_numeric(data['high'])
    data['low'] = pd.to_numeric(data['low'])
    data['volume'] = pd.to_numeric(data['volume'])

    macd, macdsignal, macdhist = talib.MACD(data['close'].values, fastperiod=fast_ma, slowperiod=slow_ma, signalperiod=9)
    data['MACD'] = macd
    data['MACD_signal'] = macdsignal
    data['MACD_hist'] = macdhist

    data['Buy_Signal'] = np.where((data['MACD'] > data['MACD_signal']), 1, 0)
    data['Sell_Signal'] = np.where((data['MACD'] < data['MACD_signal']), 1, 0)

    return data

def calculate_win_rate(df):
    win_trades = len(df[(df['Buy_Signal'].shift() == 1) & (df['close'] > df['close'].shift())]) + len(df[(df['Sell_Signal'].shift() == 1) & (df['close'] < df['close'].shift())])
    total_trades = len(df[df['Buy_Signal'].shift() == 1]) + len(df[df['Sell_Signal'].shift() == 1])
    win_rate = win_trades / total_trades * 100

    return win_rate

df = scalping_bot('ETHUSDT', '1m', '1', 12, 26)
win_rate = calculate_win_rate(df)
print(f"Win rate: {win_rate:.2f}%")
