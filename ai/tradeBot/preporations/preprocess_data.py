import pandas as pd

# Загружаем данные из файла
df = pd.read_csv('ETH_USDT_data_15m.csv')

# Преобразуем 'timestamp' обратно в datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Создаем новый признак: скользящее среднее за 5 периодов
df['ma_5'] = df['close'].rolling(window=5).mean()

# Удаляем первые 4 строки, где скользящее среднее не определено
df = df.dropna()

# Сохраняем предобработанные данные
df.to_csv('ETH_USDT_data_15m_preprocessed.csv', index=False)
