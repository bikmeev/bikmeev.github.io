import ccxt
import pandas as pd

# Инициализируем биржу
exchange = ccxt.binance({
    'enableRateLimit': True,
})

# Получаем исторические данные
data = exchange.fetch_ohlcv('ETH/USDT', '5m')

# Преобразуем данные в DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Конвертируем timestamp в datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Сохраняем данные в файл
df.to_csv('ETH_USDT_data_5m_11_07_2023.csv', index=False)
