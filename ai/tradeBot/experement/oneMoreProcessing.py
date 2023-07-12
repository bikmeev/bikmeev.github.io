import pandas as pd

# Загружаем предобработанные данные
df = pd.read_csv('ETH_USDT_data_1h_preprocessed.csv')

# Создаем целевую переменную
df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

# Удаляем последнюю строку, где целевая переменная не определена
df = df[:-1]
