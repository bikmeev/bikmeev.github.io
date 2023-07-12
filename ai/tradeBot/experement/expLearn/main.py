from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb
import pandas as pd

# Загрузите ваши данные
df = pd.read_csv('ETH_USDT_data_1h.csv')

# Разделяем данные на признаки (X) и целевую переменную (y)
X = df.drop('target', axis=1)
y = df['target']

# Разделяем данные на обучающую и тестовую выборку
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создаем и обучаем модель
model = xgb.XGBClassifier(use_label_encoder=False)
model.fit(X_train, y_train)

# Предсказываем целевую переменную на тестовой выборке
y_pred = model.predict(X_test)

# Считаем и выводим точность модели
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy}')
