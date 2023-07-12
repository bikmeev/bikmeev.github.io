import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from keras.optimizers import Adam
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
import talib

from keras.models import load_model

# Загрузка данных
data = pd.read_csv('ETH_USDT_data_15m.csv')
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Предобработка данных
data = data.set_index('timestamp')

# Calculate ATR and EMA
data['ATR'] = talib.ATR(data['high'].values, data['low'].values, data['close'].values, timeperiod=14)
data['EMA'] = talib.EMA(data['close'].values, timeperiod=30)

# Drop the NaN values
data = data.dropna()

closing_prices = data['close'].values.reshape(-1, 1)
atr_values = data['ATR'].values.reshape(-1, 1)
ema_values = data['EMA'].values.reshape(-1, 1)

closing_scaler = MinMaxScaler()
scaled_closing_prices = closing_scaler.fit_transform(closing_prices)

prices = np.concatenate([scaled_closing_prices, atr_values, ema_values], axis=1)

# Подготовка данных для LSTM
X = []
y = []
for i in range(60, len(prices)):
    X.append(prices[i-60:i])
    y.append(prices[i, 0])
X, y = np.array(X), np.array(y)

# Разделение на обучающую и тестовую выборки
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Изменение размерности данных
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], X_train.shape[2]))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], X_test.shape[2]))

# Создание модели LSTM
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=1))

# Компиляция и обучение модели
model.compile(optimizer=Adam(), loss='mean_squared_error')
model.fit(X_train, y_train, epochs=50, batch_size=32)

# Прогнозирование
predictions = model.predict(X_test)
predictions = closing_scaler.inverse_transform(predictions)
y_test = closing_scaler.inverse_transform(y_test.reshape(-1, 1))

# Расчет метрик
mse = mean_squared_error(y_test, predictions)
rmse = sqrt(mse)

print(f'MSE: {mse}')
print(f'RMSE: {rmse}')

# Вывод результатов
plt.plot(y_test, color='blue', label='Actual')
plt.plot(predictions, color='red', label='Predicted')
plt.title('Cryptocurrency Price Prediction')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()

# Сохранение модели
model.save('v0.0.5.15m.h5')
