from binance.client import Client
from binance.enums import *
import time
import numpy as np
from keras.models import load_model
import mysql.connector
import threading
from binance.exceptions import BinanceAPIException
import atexit

def stop_bot():
    update_status("Stopped")

# Регистрирует функцию stop_bot, чтобы вызвать ее при завершении
atexit.register(stop_bot)

model = load_model('v0.0.4.15m.h5')

#настроки<...
SOME_THRESHOLD = 0.25  # Войти в позицию, если модель предсказывает увеличение цены на 1% или больше
SOME_OTHER_THRESHOLD = -0.25  # Продать, если модель предсказывает снижение цены на 1% или больше

QUANTITY = 1  # количество единиц актива для покупки или продажи

#стоп и тейк
TPperc = 0.95 # 5% ниже цены
SLperc = 1.05 # 5% выше цены

# Настройки BinanceTestnet
# TEST NET
testnet_api_key = '8H6PWP7g0sWfyCidxITrBrheA9mWFsVWpLh2UxU67N71YXUs7zfxZ8HtsQITLdLs'
testnet_api_secret = 'z7lZOurJIA4KTXk1QU2lhFrhZ8OcwyBoBu5bRtTYi9CgEUz6DyMG9tIZWZB2kbWJ'

# подключение к бд
DATABASE_URL = "mysql://b1kme1ch_games:xF9cdPyP@intelektus.ru/b1kme1ch_games"

# создание таблиц и столбцов в них соответственно
cnx = mysql.connector.connect(
  host="intelektus.ru",
  user="b1kme1ch_games",
  password="xF9cdPyP",
  database="b1kme1ch_games"
)

cursor = cnx.cursor()

try:
    # Создание таблицы для хранения статуса бота, если она еще не существует
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bot_status (
        id INT AUTO_INCREMENT PRIMARY KEY,
        status VARCHAR(255) NOT NULL
    )
    """)

    # Создание таблицы для хранения статистики, если она еще не существует
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS statistics (
        id INT AUTO_INCREMENT PRIMARY KEY,
        win_rate FLOAT,
        total_trades INT,
        successful_trades INT,
        unsuccessful_trades INT,
        days_operating INT,
        trades_per_day FLOAT
    )
    """)

    # Создание таблицы для хранения открытых ордеров, если она еще не существует
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS open_orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id VARCHAR(255) NOT NULL,
        symbol VARCHAR(255),
        side VARCHAR(255),
        price FLOAT,
        stop_price FLOAT,
        take_profit_price FLOAT
    )
    """)

    cnx.commit()

except mysql.connector.Error as err:
    print("Возникла ошибка: {}".format(err))

finally:
    #cnx.close()
    print("database chech success")

#cnx.commit()
#cnx.close()

# Инициализация клиента Binance для Testnet
client = Client(testnet_api_key, testnet_api_secret)

client.API_URL = 'https://testnet.binance.vision/api'  # Binance Testnet URL

#...>настроки

cursor = cnx.cursor()

# Инициализация статистики
bot_statistics = {
    "win_rate": 0,
    "total_trades": 0,
    "successful_trades": 0,
    "unsuccessful_trades": 0,
    "days_operating": 0,
    "trades_per_day": 0,
}

bot_status = "Stopped"

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


def update_status(status):
    global bot_status
    bot_status = status

    cursor.execute(f"UPDATE bot_status SET status = '{status}' WHERE id = 1;")
    cnx.commit()
    print("update_status done")
    print(status)


def update_statistics(statistics):
    cursor.execute(
        f"""UPDATE statistics SET
        win_rate = {statistics['win_rate']},
        total_trades = {statistics['total_trades']},
        successful_trades = {statistics['successful_trades']},
        unsuccessful_trades = {statistics['unsuccessful_trades']},
        days_operating = {statistics['days_operating']},
        trades_per_day = {statistics['trades_per_day']}
        WHERE id = 1;"""
    )
    cnx.commit()


# В самом начале работы бота устанавливаем его статус в 'Running'
update_status("Running")

# Эта функция будет запущена в отдельном потоке и будет проверять ордера каждую минуту
def update_orders():
    while True:
        try:
            open_orders = client.futures_get_open_orders(symbol="ETHUSDT")
            for order in open_orders:
                # Проверьте, существует ли этот заказ в базе данных, и обновите его при необходимости
                # В этом примере предполагается, что у вас есть таблица 'orders' с полями 'order_id' и 'status'
                cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order['orderId'],))
                result = cursor.fetchone()

                if result is None:
                    # Заказа нет в базе данных, добавим его
                    cursor.execute("INSERT INTO orders (order_id, status) VALUES (%s, %s)",
                                   (order['orderId'], order['status']))
                else:
                    # Заказ уже есть в базе данных, обновим его статус
                    cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s",
                                   (order['status'], order['orderId']))

                cnx.commit()

            # Подождите минуту перед следующей проверкой
            time.sleep(60)
        except BinanceAPIException as e:
            print(f"Ошибка при обновлении ордеров: {e}")
            time.sleep(60)  # Если произошла ошибка, подождите минуту перед повторной попыткой

# Запуск обновления ордеров в отдельном потоке
orders_thread = threading.Thread(target=update_orders)
orders_thread.start()

# Запуск бота
while True:
    predict_and_trade()

    # Обновляем статистику каждый цикл
    update_statistics(bot_statistics)

    time.sleep(840)

cnx.close()