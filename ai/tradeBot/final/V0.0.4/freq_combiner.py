import numpy as np
from keras.models import load_model
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

# Load the trading data
data = pd.read_csv('BTC_USDT_data_15m.csv')
data['close'] = data['close'].pct_change()  # Calculate the percentage change in price
data.dropna(how='any', inplace=True)  # Remove NaN rows

# Load the trained model
model = load_model('v0.0.6.15m.h5')

# Define the constant parameters
take_profit = 0.001
stop_loss = -0.01
predPers = 0.002

# Define the range of possible values for each parameter
analysis_frequency_range = np.arange(1, 61, 1)  # Analyze the market every 1 to 60 candles

# Placeholder for the best frequency and its statistics
best_frequency = 0
best_win_rate = 0
lowest_trades = np.inf

# Placeholder for the most beneficial frequency and its statistics
most_beneficial_frequency = 0
best_benefit = -np.inf

# Lists to keep track of the benefit and win rate at each frequency
benefit_list = []
win_rate_list = []

# Adding a tqdm progress bar
for analysis_frequency in tqdm(analysis_frequency_range):
    # Initialize statistics for this frequency
    statistics = {
        'total_trades': 0,
        'successful_trades': 0,
        'unsuccessful_trades': 0,
        'profit': 0.0
    }

    # Run the simulation with the current frequency
    for i in range(60, len(data) - 1, analysis_frequency):
        price_data = data['close'].values[i - 60:i].reshape(1, -1, 1)
        prediction = model.predict(price_data, verbose=0)[0][0]

        if prediction > predPers:
            open_price = data['close'][i]
            statistics['total_trades'] += 1
            for j in range(i + 1, len(data)):
                price_change = data['close'][j] - open_price
                if price_change >= take_profit:
                    statistics['successful_trades'] += 1
                    statistics['profit'] += take_profit
                    break
                elif price_change <= stop_loss:
                    statistics['unsuccessful_trades'] += 1
                    statistics['profit'] += stop_loss
                    break

    # Calculate the win rate for this frequency
    if statistics['total_trades'] != 0:
        win_rate = (statistics['successful_trades'] / statistics['total_trades']) * 100

    # Check if this frequency is better than the current best
    if win_rate > best_win_rate or (win_rate == best_win_rate and statistics['total_trades'] < lowest_trades):
        best_win_rate = win_rate
        best_frequency = analysis_frequency
        lowest_trades = statistics['total_trades']

    # Check if this frequency is more beneficial than the current most beneficial
    benefit = win_rate * statistics['profit'] / statistics['total_trades']
    if benefit > best_benefit:
        best_benefit = benefit
        most_beneficial_frequency = analysis_frequency

    # Add the benefit and win rate to the lists
    benefit_list.append(benefit)
    win_rate_list.append(win_rate)

# Print the best frequency and its win rate
print(f'Best frequency: {best_frequency}')
print(f'Best win rate: {best_win_rate}%')
print(f'Lowest trades: {lowest_trades}')
print(f'Most beneficial frequency: {most_beneficial_frequency}')
print(f'Best benefit: {best_benefit}')

# Plot the benefit over different frequencies
plt.figure(figsize=(12, 6))
plt.plot(analysis_frequency_range, benefit_list, label='Benefit')
plt.plot(analysis_frequency_range, win_rate_list, label='Win Rate')
plt.xlabel('Frequency')
plt.ylabel('Value')
plt.title('Benefit and Win Rate over different frequencies')
plt.legend()
plt.show()
