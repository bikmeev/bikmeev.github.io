import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier
from sklearn.model_selection import GridSearchCV
import ta
import numpy as np
import talib

# load data
df = pd.read_csv('ETH_USDT_data_15m.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# load volume data and set timestamp as index
df_volume = pd.read_csv('ETH_USDT_volume_data_15m.csv')
df_volume['timestamp'] = pd.to_datetime(df_volume['timestamp'])
df_volume.set_index('timestamp', inplace=True)

# add volume data
df['volume'] = df_volume['volume']

# calculate technical indicators
df['RSI'] = ta.momentum.rsi(df['close'], window=14)
df['MACD'] = ta.trend.macd_diff(df['close'], window_slow=26, window_fast=12)
df['MA'] = ta.volatility.bollinger_mavg(df['close'], window=20)
df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)

# Additional technical indicators
df['CCI'] = ta.trend.cci(df['high'], df['low'], df['close'], window=20)
df['SMA'] = ta.trend.sma_indicator(df['close'], window=20)
df['EMA'] = ta.trend.ema_indicator(df['close'], window=20)

# Create a candlestick pattern
df['DOJI'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
df['HAMMER'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])

# Support line slope
df['slope'] = (df['low'] - df['low'].shift(10)) / 10

# drop NA values
df = df.dropna()

# define target variable
df['target'] = df['close'].shift(-1) > df['close']
df['target'] = df['target'].astype(int)
df = df.dropna()

# split data into X and y
X = df.drop('target', axis=1)
y = df['target']

# split data into train and testsets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)

# hyperparameter tuning with GridSearchCV
param_grid = {
    'max_depth': [3, 4, 5],
    'learning_rate': [0.1, 0.01, 0.05],
    'n_estimators': [100, 200, 500],
    'gamma': [0, 0.5, 1],
}

grid_clf = GridSearchCV(xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss'), param_grid, cv=3, n_jobs=-1)
grid_clf.fit(X_train, y_train)

# Best model
best_model = grid_clf.best_estimator_

# BaggingClassifier
bagging_clf = BaggingClassifier(best_model, n_estimators=10, max_samples=0.8, max_features=0.8)
bagging_clf.fit(X_train, y_train)

# make predictions
y_pred = bagging_clf.predict(X_test)

# evaluate predictions
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
