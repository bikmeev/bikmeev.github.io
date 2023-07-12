import numpy as np
import itertools
from keras.models import load_model
import pandas as pd
from tqdm import tqdm

# Load the trading data
data = pd.read_csv('ETH_USDT_data_15m.csv')
data['close'] = data['close'].pct_change()  # Calculate the percentage change in price
data.dropna(how='any', inplace=True)  # Remove NaN rows

# Load the trained model
model = load_model('v0.0.6.15m.h5')

# Define the range of possible values for each parameter
take_profit_range = np.arange(0.001, 0.01, 0.001)
stop_loss_range = np.arange(-0.01, -0.001, 0.001)
predPers_range = np.arange(0.002, 0.022, 0.002)

# Generate all possible combinations of parameters
parameter_combinations = list(itertools.product(take_profit_range, stop_loss_range, predPers_range))

# Placeholder for the best combination and its statistics
best_combination = None
best_win_rate = 0

# Adding a tqdm progress bar
for take_profit, stop_loss, predPers in tqdm(parameter_combinations):
    # Initialize statistics for this combination
    statistics = {
        'total_trades': 0,
        'successful_long_trades': 0,
        'unsuccessful_long_trades': 0,
        'successful_short_trades': 0,
        'unsuccessful_short_trades': 0,
        'long_win_rate': 0.0,
        'short_win_rate': 0.0,
        'general_win_rate': 0.0,
        'max_up': 0.0,
        'max_down': 0.0,
        'avg_up': 0.0,
        'avg_down': 0.0,
        'up_moves': [],
        'down_moves': []
    }

    # Run the simulation with the current combination (your existing code here)
    for i in range(60, len(data) - 1):
        price_data = data['close'].values[i - 60:i].reshape(1, -1, 1)
        prediction = model.predict(price_data, verbose=0)[0][0]

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

    # Calculate the general win rate for this combination
    if statistics['total_trades'] != 0:
        statistics['general_win_rate'] = ((statistics['successful_long_trades'] + statistics['successful_short_trades']) /
                                          statistics['total_trades']) * 100

    # Check if this combination is better than the current best
    if statistics['general_win_rate'] > best_win_rate:
        best_win_rate = statistics['general_win_rate']
        best_combination = (take_profit, stop_loss, predPers)

# Print the best combination and its win rate
print(f'Best combination: take_profit = {best_combination[0]}, stop_loss = {best_combination[1]}, predPers = {best_combination[2]}')
print(f'Best win rate: {best_win_rate}%')
