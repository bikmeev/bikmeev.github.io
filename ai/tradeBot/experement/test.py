import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Загружаем данные
df = pd.read_csv('ETH_USDT_data_1h.csv')

print(df.columns)
