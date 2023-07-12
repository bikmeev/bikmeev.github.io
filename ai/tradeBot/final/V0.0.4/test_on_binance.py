import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from keras.models import load_model
import pandas as pd

# Загружаем обученную модель
model = load_model('v0.0.6.5m.h5')

# Вставьте ваши ключи API здесь
api_key = 'lEhzudfsTWE0FcaZzf4K7YrmNcfN8m80cvsgkxPhUzo0Df4vXO1tZNNdvYixfFsb'
api_secret = 'jdZiv0CXSl5z70k1imrIafCZRNk5YPCaeMXtTPR5a9HNqEEadhtQA7bD3G2zLA2c'

# Базовый и котируемый активы
base_asset = 'BTC'
quote_asset = 'USDT'
symbol = base_asset + quote_asset

# Параметры для каждой торговой операции
percentage_of_balance_to_trade = 0.3  # 10% от доступного баланса

leverage = 30  # Плечо

fixed_margin = 11.0

quantity12 = 0.003
stop_loss = 0.01  # Stop-loss (в процентах от стоимости открытия)
take_profit = 0.001  # Take-profit (в процентах от стоимости открытия)
predValue0 = 0.002

# Создаем клиента Binance
client = Client(api_key, api_secret)

def get_data():
    """Получение данных для прогноза."""
    candles = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
    data = pd.DataFrame(candles, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    data['Open time'] = pd.to_datetime(data['Open time'], unit='ms')
    data.set_index('Open time', inplace=True, drop=False)

    # Преобразуем только нужные столбцы во float, оставляем 'Open time' нетронутым
    for col in ['Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume']:
        data[col] = data[col].astype(float)

    return data['Close'].values[-60:].reshape(1, -1, 1)


def get_precision(symbol):
    """Получение точности для данного символа."""
    info = client.futures_exchange_info()
    for pair in info['symbols']:
        if pair['symbol'] == symbol:
            return pair['quantityPrecision']
    return None

def predict(data):
    """Получение прогноза от обученной модели."""
    prediction = model.predict(data)
    return prediction

def get_balance(asset):
    """Получение доступного баланса для данного актива."""
    futures_account = client.futures_account_balance()
    balance = next((item for item in futures_account if item["asset"] == asset), None)
    return float(balance['balance']) if balance is not None else 0.0

def run_bot():
    print(f"баланс кошелька: {get_balance(quote_asset)} USDT")
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    # client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')

    while True:
        # Получаем данные для прогноза
        data = get_data()

        # Получаем прогноз
        prediction = predict(data)

        # Получаем доступный баланс
        balance = get_balance(quote_asset)

        # Расчет количества актива, которое будем покупать/продавать
        precision = get_precision(symbol)

        # Расчет количества актива на основе фиксированной маржи
        quantityPre = fixed_margin

        quantity = round(quantityPre, precision)

        precision = get_precision(symbol)

        quantityPre = (balance * percentage_of_balance_to_trade) / 100  # <- Here we calculate the quantity in contracts

        quantity = round(quantityPre, precision)

        if prediction > predValue0:
            # Открываем позицию в лонг
            try:
                #client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')
                order = client.futures_create_order(
                    symbol=symbol,
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity12,
                    reduceOnly='false',
                    newOrderRespType='FULL'
                )

                # Получаем ID ордера
                orderId = order['orderId']

                # Ждем 10 секунд
                time.sleep(2)

                # Получаем обновленную информацию об ордере
                order = client.futures_get_order(symbol=symbol, orderId=orderId)

                # Проверяем, был ли ордер исполнен
                if order['status'] == 'FILLED':
                    entryPrice = float(order['avgPrice'])
                else:
                    print(f"Order not filled. Order response: {order}")

                print(f"Opened LONG position. Entry price: {entryPrice}")
                # Установка stop loss и take profit
                client.futures_create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL,
                    type='STOP_MARKET',
                    quantity=quantity12,
                    stopPrice=round(entryPrice * (1 - stop_loss), 1),
                    newOrderRespType='FULL',
                    closePosition=True,
                )
                print(f"Set STOP LOSS for LONG at: {entryPrice * (1 - stop_loss)}")

                client.futures_create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL,
                    type='TAKE_PROFIT_MARKET',
                    quantity=quantity12,
                    stopPrice=round(entryPrice * (1 + take_profit), 1),
                    newOrderRespType='FULL',
                    closePosition=True,
                )
                print(f"Set TAKE PROFIT for LONG at: {entryPrice * (1 + take_profit)}")

            except BinanceAPIException as e:
                print(e)
                print(quantity)

        elif prediction < predValue0:
            # Открываем позицию в шорт
            try:
                #client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')
                order = client.futures_create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity,
                    reduceOnly='false',
                    newOrderRespType='FULL'
                )
                orderId = order['orderId']
                entryPrice = float(order['fills'][0]['price'])
                print(f"Opened SHORT position. Entry price: {entryPrice}")
                # Установка stop loss и take profit
                client.futures_create_order(
                    symbol=symbol,
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_STOP_MARKET,
                    quantity=quantity,
                    stopPrice=entryPrice * (1 + stop_loss),
                    newOrderRespType='FULL',
                    reduceOnly='true',
                )
                print(f"Set STOP LOSS for SHORT at: {entryPrice * (1 + stop_loss)}")
                client.futures_create_order(
                    symbol=symbol,
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_TAKE_PROFIT_MARKET,
                    quantity=quantity,
                    stopPrice=entryPrice * (1 - take_profit),
                    newOrderRespType='FULL',
                    reduceOnly='true',
                )
                print(f"Set TAKE PROFIT for SHORT at: {entryPrice * (1 - take_profit)}")
            except BinanceAPIException as e:
                print(e)

        time.sleep(3000)  # В данном случае задержка составляет 3 минуты

# Запускаем бота
run_bot()
