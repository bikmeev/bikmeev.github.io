import pandas as pd
import numpy as np
from keras.models import load_model
from tqdm import tqdm

# Загружаем модель
model = load_model('v0.0.4.15m.h5')

# Загрузка данных
data = pd.read_csv('ETH_USDT_data_15m_10_07_2023.csv')

# Константы
SOME_THRESHOLD = 0.025
SOME_OTHER_THRESHOLD = -0.025
LEVERAGE = 2
PRICE_CHANGE_FOR_CLOSE = 0.05

# Обработка данных
data['close'] = data['close'].pct_change()  # Рассчитываем процентное изменение цены
data.dropna(inplace=True)  # Удаляем NaN значения

# Статистика
statistics = {
    "total_trades": 0,
    "successful_trades": 0,
    "unsuccessful_trades": 0,
    "win_rate": 0.0
}

# Симуляция торгов
for i in tqdm(range(60, len(data))):
    # Обработка данных для модели
    price_data = data['close'].values[i - 60:i].reshape(1, -1, 1)

    # Предсказание
    prediction = model.predict(price_data, verbose=0)

    # Если прогноз выше порога, открываем позицию
    if prediction > SOME_THRESHOLD:
        # Проверяем, достигнет ли цена изменения на 5%
        for j in range(i, len(data)):
            # Если цена увеличивается на 5% или более, мы закрываем позицию
            if data['close'].values[j] >= PRICE_CHANGE_FOR_CLOSE:
                statistics["successful_trades"] += 1
                break
            # Если цена уменьшается на 5% или более, мы закрываем позицию
            elif data['close'].values[j] <= -PRICE_CHANGE_FOR_CLOSE:
                statistics["unsuccessful_trades"] += 1
                break

        statistics["total_trades"] += 1

    # Если прогноз ниже порога, открываем позицию
    elif prediction < SOME_OTHER_THRESHOLD:
        # Проверяем, достигнет ли цена изменения на 5%
        for j in range(i, len(data)):
            # Если цена уменьшается на 5% или более, мы закрываем позицию
            if data['close'].values[j] <= -PRICE_CHANGE_FOR_CLOSE:
                statistics["successful_trades"] += 1
                break
            # Если цена увеличивается на 5% или более, мы закрываем позицию
            elif data['close'].values[j] >= PRICE_CHANGE_FOR_CLOSE:
                statistics["unsuccessful_trades"] += 1
                break

        statistics["total_trades"] += 1

# Рассчитываем win rate
if statistics["total_trades"] > 0:
    statistics["win_rate"] = statistics["successful_trades"] / statistics["total_trades"]

print(statistics)
