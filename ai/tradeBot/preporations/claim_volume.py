import ccxt
import pandas as pd

# Инициализируем биржу
exchange = ccxt.binance({
    'enableRateLimit': True,
})

# Получаем исторические данные
data = exchange.fetch_ohlcv('ETH/USDT', '1h')

# Преобразуем данные в DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Конвертируем timestamp в datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Оставляем только данные об объеме
volume_data = df[['timestamp', 'volume']]

# Сохраняем данные в файл
volume_data.to_csv('ETH_USDT_volume_data_1h.csv', index=False)
