import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from keras.optimizers import Adam
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
from keras.layers import LSTM, Dense
from keras.models import Sequential
from sklearn.preprocessing import StandardScaler

from keras.models import load_model

# Загрузка модели
#model = load_model('my_model.h5')

# Загрузка данных
data = pd.read_csv('ETH_USDT_data_15m.csv')
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Предобработка данных
data = data.set_index('timestamp')
prices = data['close'].values.reshape(-1, 1)

# Нормализация данных
scaler = MinMaxScaler()
prices = scaler.fit_transform(prices)

# Подготовка данных для LSTM
X = []
y = []
for i in range(60, len(prices)):
    X.append(prices[i-60:i, 0])
    y.append(prices[i, 0])
X, y = np.array(X), np.array(y)

# Разделение на обучающую и тестовую выборки
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Изменение размерности данных
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1, activation='tanh'))  # Здесь мы используем tanh вместо ReLU
model.compile(optimizer='adam', loss='mean_squared_error')

# Создание модели LSTM
#model = Sequential()
#model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
#model.add(Dropout(0.2))
#model.add(LSTM(units=50))
#model.add(Dropout(0.2))
#model.add(Dense(units=1))

# Компиляция и обучение модели
model.compile(optimizer=Adam(), loss='mean_squared_error')
model.fit(X_train, y_train, epochs=100, batch_size=32)

# Прогнозирование
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)
y_test = scaler.inverse_transform(y_test.reshape(-1, 1))

# Расчет метрик
mse = mean_squared_error(y_test, predictions)
rmse = sqrt(mse)

tolerance = 0.3  # определите свою собственную толерантность
accurate_predictions = np.abs(predictions - y_test) <= tolerance
regression_accuracy = np.sum(accurate_predictions) / len(y_test)

print(f'MSE: {mse}')
print(f'RMSE: {rmse}')

print(f'Regression Accuracy: {regression_accuracy}')

# Вывод результатов
plt.plot(y_test, color='blue', label='Actual')
plt.plot(predictions, color='red', label='Predicted')
plt.title('Cryptocurrency Price Prediction')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()

# Сохранение модели
model.save('v0.0.6.15m.h5')