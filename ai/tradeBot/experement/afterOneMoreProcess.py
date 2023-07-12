import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import ta

# load data
df = pd.read_csv('ETH_USDT_data_15m.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# load volume data and set timestamp as index
df_volume = pd.read_csv('ETH_USDT_volume_data_15m.csv')
df_volume['timestamp'] = pd.to_datetime(df_volume['timestamp'])
df_volume.set_index('timestamp', inplace=True)

# Check the first few rows of volume data
#print("Volume data:")
#print(df_volume.head())

# Check the first few rows of price data
#print("Price data:")
#print(df.head())

# add volume data
df['volume'] = df_volume['volume']

# Check the first few rows of the combined data
#print("Combined data:")
#print(df.head())

# calculate technical indicators
df['RSI'] = ta.momentum.rsi(df['close'], window=14)
df['MACD'] = ta.trend.macd_diff(df['close'], window_slow=26, window_fast=12)
df['MA'] = ta.volatility.bollinger_mavg(df['close'], window=20)
df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)

# Check for any missing values
#print(df.isnull().sum())

# drop NA values
df = df.dropna()

# define target variable
df['target'] = df['close'].shift(-1) > df['close']
df['target'] = df['target'].astype(int)
df = df.dropna()

# split data into X and y
X = df.drop('target', axis=1)
y = df['target']

# split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)

# train model
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

# make predictions
y_pred = model.predict(X_test)

# evaluate predictions
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
