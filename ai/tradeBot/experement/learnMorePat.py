import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb
import ta

# Загружаем данные
df = pd.read_csv('ETH_USDT_data_1h.csv')

# Вычисляем индикаторы
df['RSI'] = ta.momentum.RSIIndicator(close = df['close'], window = 14).rsi()
df['MACD'] = ta.trend.MACD(close = df['close'], window_slow = 26, window_fast = 12).macd_diff()
df['Bollinger_band_width'] = ta.volatility.BollingerBands(close = df['close'], window = 20).bollinger_wband()

# Удаляем строки с NaN значениями
df = df.dropna()

# Создаем целевую переменную
df['target'] = df['close'].shift(-1) - df['close'] > 0
df = df.dropna()

# Удаляем столбец 'timestamp'
df = df.drop('timestamp', axis=1)

# Разделяем данные на признаки (X) и целевую переменную (y)
X = df.drop('target', axis=1)
y = df['target']

# Разделяем данные на обучающую и тестовую выборку
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создаем и обучаем модель
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

# Предсказываем целевую переменную на тестовой выборке
y_pred = model.predict(X_test)

# Считаем и выводим точность модели
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy}')
