from binance.client import Client
from binance.exceptions import BinanceAPIException

api_key = 'ВАШ_КЛЮЧ_API'
api_secret = 'ВАШ_СЕКРЕТНЫЙ_КЛЮЧ_API'

client = Client(api_key, api_secret)

try:
    # Получение информации о балансе
    account_info = client.futures_account()
    print("Баланс на Binance Futures:")
    for asset in account_info['assets']:
        if float(asset['balance']) > 0:
            print(f"Актив: {asset['asset']}, Баланс: {asset['balance']}")
except BinanceAPIException as e:
    print(f"Ошибка при работе с Binance API: {e}")
except Exception as e:
    print(f"Неизвестная ошибка: {e}")
