import pandas as pd
from tqdm import tqdm
from keras.models import load_model
import matplotlib.pyplot as plt

# Загрузка обученной модели
model = load_model('v0.0.5.15m.h5')

# Загрузка и подготовка данных
data = pd.read_csv('ETH_USDT_data_15m_10_07_2023.csv')

data['close'] = data['close'].pct_change()  # Рассчитываем процентное изменение цены
data.dropna(how='any', inplace=True)  # Удаляем NaN строки

# Инициализация статистики
statistics = {
    'total_trades': 0,
    'successful_long_trades': 0,
    'unsuccessful_long_trades': 0,
    'successful_short_trades': 0,
    'unsuccessful_short_trades': 0,
    'long_win_rate': 0.0,
    'short_win_rate': 0.0,
    'general_win_rate': 0.0,  # Добавлено
    'max_up': 0.0,
    'max_down': 0.0,
    'avg_up': 0.0,
    'avg_down': 0.0,
    'up_moves': [],
    'down_moves': []
}

# Задаем уровни take_profit и stop_loss
take_profit = 0.006  # 0.6% profit
stop_loss = -0.006  # 0.6% loss

predPers = 0.006

# Симуляция торгов
for i in tqdm(range(60, len(data) - 1)):
    # Обработка данных для модели
    price_data = data['close'].values[i - 60:i + 1].reshape(1, -1, 1)



    # Предсказание
    prediction = model.predict(price_data, verbose=0)[0][0]

    # Если прогноз выше порога, открываем позицию в лонг
    if prediction > predPers:
        open_price = data['close'][i]
        statistics['total_trades'] += 1

        for j in range(i + 1, len(data)):
            price_change = data['close'][j] - open_price

            if price_change > statistics['max_up']:
                statistics['max_up'] = price_change
                statistics['up_moves'].append(price_change)

            if price_change >= take_profit:
                statistics['successful_long_trades'] += 1
                break
            elif price_change <= stop_loss:
                statistics['unsuccessful_long_trades'] += 1
                break

    # Если прогноз ниже отрицательного порога, открываем позицию в шорт
    elif prediction < -predPers:
        open_price = data['close'][i]
        statistics['total_trades'] += 1

        for j in range(i + 1, len(data)):
            price_change = data['close'][j] - open_price

            if price_change < statistics['max_down']:
                statistics['max_down'] = price_change
                statistics['down_moves'].append(price_change)

            if price_change <= stop_loss:
                statistics['successful_short_trades'] += 1
                break
            elif price_change >= take_profit:
                statistics['unsuccessful_short_trades'] += 1
                break

# Выводим статистику
statistics['long_win_rate'] = (statistics['successful_long_trades'] / (
            statistics['successful_long_trades'] + statistics['unsuccessful_long_trades'])) * 100 if (statistics[
                                                                                                          'successful_long_trades'] +
                                                                                                      statistics[
                                                                                                          'unsuccessful_long_trades']) != 0 else 0
statistics['short_win_rate'] = (statistics['successful_short_trades'] / (
            statistics['successful_short_trades'] + statistics['unsuccessful_short_trades'])) * 100 if (statistics[
                                                                                                            'successful_short_trades'] +
                                                                                                        statistics[
                                                                                                            'unsuccessful_short_trades']) != 0 else 0
statistics['general_win_rate'] = ((statistics['successful_long_trades'] + statistics['successful_short_trades']) /
                                  statistics['total_trades']) * 100 if statistics[
                                                                           'total_trades'] != 0 else 0  # Добавлено
statistics['avg_up'] = sum(statistics['up_moves']) / len(statistics['up_moves']) if statistics['up_moves'] else 0
statistics['avg_down'] = sum(statistics['down_moves']) / len(statistics['down_moves']) if statistics[
    'down_moves'] else 0
print(statistics)
