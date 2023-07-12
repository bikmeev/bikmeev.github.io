from binance.client import Client
from binance.enums import *
import time
import numpy as np
from keras.models import load_model

model = load_model('v0.0.4.15m.h5')

#настроки<...
SOME_THRESHOLD = 0.25  # Войти в позицию, если модель предсказывает увеличение цены на 1% или больше
SOME_OTHER_THRESHOLD = -0.25  # Продать, если модель предсказывает снижение цены на 1% или больше

QUANTITY = 1  # количество единиц актива для покупки или продажи

#стоп и тейк
TPperc = 0.95 # 5% ниже цены
SLperc = 1.05 # 5% выше цены

# Настройки Binance Testnet
testnet_api_key = '8H6PWP7g0sWfyCidxITrBrheA9mWFsVWpLh2UxU67N71YXUs7zfxZ8HtsQITLdLs'
testnet_api_secret = 'z7lZOurJIA4KTXk1QU2lhFrhZ8OcwyBoBu5bRtTYi9CgEUz6DyMG9tIZWZB2kbWJ'

# Инициализация клиента Binance для Testnet
client = Client(testnet_api_key, testnet_api_secret)

client.API_URL = 'https://testnet.binance.vision/api'  # Binance Testnet URL

#...>настроки

# Инициализация клиента Binance
#client = Client(api_key='8H6PWP7g0sWfyCidxITrBrheA9mWFsVWpLh2UxU67N71YXUs7zfxZ8HtsQITLdLs', api_secret='z7lZOurJIA4KTXk1QU2lhFrhZ8OcwyBoBu5bRtTYi9CgEUz6DyMG9tIZWZB2kbWJ')


def load_data():
    # Используйте Binance API, чтобы получить последние данные
    candles = client.futures_klines(symbol='ETHUSDT', interval=Client.KLINE_INTERVAL_15MINUTE)

    # Преобразуйте данные в формат, подходящий для вашей модели
    data = preprocess_data(candles)

    return data

def preprocess_data(candles):
    # Преобразование данных свечи в удобный формат
    data = []
    for candle in candles[-60:]:  # Возьмите только последние 60 свечей
        data.append([float(candle[1])])

    return np.array(data).reshape(1, -1, 1)

def place_order(side, quantity, symbol, price, stopPrice, takeProfitPrice):
    """
    Размещает заказ на Binance.
    """
    try:
        print(f"Отправка {side} заказа на {symbol} за {quantity}...")
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=price)
        print(order)

        if side == SIDE_BUY:
            stop_order_side = SIDE_SELL
        else:
            stop_order_side = SIDE_BUY

        # Разместить ордер на stop loss
        stop_loss_order = client.futures_create_order(
            symbol=symbol,
            side=stop_order_side,
            type=ORDER_TYPE_STOP_MARKET,
            quantity=quantity,
            stopPrice=stopPrice)
        print(stop_loss_order)

        # Разместить ордер на take profit
        take_profit_order = client.futures_create_order(
            symbol=symbol,
            side=stop_order_side,
            type=ORDER_TYPE_TAKE_PROFIT_MARKET,
            quantity=quantity,
            stopPrice=takeProfitPrice)
        print(take_profit_order)

    except Exception as e:
        print("Произошла ошибка при отправке заказа:", e)
        return False

    return True

def predict_and_trade():
    """
    Использует модель для прогнозирования и осуществления торговых операций.
    """
    # Загрузка последних данных
    # (вместо этого вы должны загрузить реальные данные с Binance API)
    data = load_data()

    # Применение модели к данным
    prediction = model.predict(data)

    # Решение о торговле на основе прогноза
    if prediction > SOME_THRESHOLD:
        # Вход в лонг
        place_order(SIDE_BUY, QUANTITY, 'ETHUSDT', price, stopPrice, takeProfitPrice)
    elif prediction < SOME_OTHER_THRESHOLD:
        # Вход в шорт
        place_order(SIDE_SELL, QUANTITY, 'ETHUSDT', price, stopPrice, takeProfitPrice)

last_price = float(client.futures_symbol_ticker(symbol="ETHUSDT")['price'])

price = last_price
stopPrice = last_price * TPperc  # 5% ниже цены
takeProfitPrice = last_price * SLperc  # 5% выше цены

# Запуск бота
while True:
    predict_and_trade()
    time.sleep(840)
