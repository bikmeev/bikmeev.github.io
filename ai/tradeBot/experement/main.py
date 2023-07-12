import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb

# Загружаем данные
df = pd.read_csv('ETH_USDT_data_1h.csv')

# Создаем новые признаки на основе исходных данных
df['high_low_diff'] = df['high'] - df['low']
df['close_open_diff'] = df['close'] - df['open']
df['volume_moving_average'] = df['volume'].rolling(window=5).mean()

# В качестве целевой переменной используем направление изменения цены
df['target'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)

# Удаляем последнюю строку, где целевая переменная не определена
df = df[:-1]

# Нормализуем данные
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df.drop(['timestamp'], axis=1))

# Переводим нормализованные данные обратно в DataFrame
df = pd.DataFrame(df_scaled, columns=df.columns.drop('timestamp'))

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
