import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime
from battery import (
    simulate_battery,
    BATTERY_EFFICIENCY,
    TRADING_COST
)

# global constant
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"           

def get_data_path():
    script_dir = Path(__file__).parent.parent

    return script_dir / 'data'


def count_negative_hours(prices: list[float]) -> int:
    if len(prices) == 0:
            raise ValueError('List can\'t be empty')
    negative_hours = 0

    for price in prices:
        if price < 0:
            negative_hours += 1

    return negative_hours


def count_zero_hours(prices: list[float]) -> int:
    if len(prices) == 0:
        raise ValueError('List can\'t be empty')

    zero_hours = 0

    for price in prices:
        if price == 0:
            zero_hours += 1

    return zero_hours


def calculate_hourly_changes(prices: list[float]) -> list[float]:
    n = len(prices)

    if n <= 1:
        raise ValueError("At least two prices are required")

    hourly_changes = []

    for i in range(n - 1):
        price_change = prices[i + 1] - prices[i]
        hourly_changes.append(price_change)

    return hourly_changes


def calculate_average_absolute_price_change(price_changes: list[float]) -> float:
    if len(price_changes) == 0:
        raise ValueError('List can\'t be empty')
    
    absolute_price_changes = []

    for price_change in price_changes:
        absolute_price_changes.append(abs(price_change))
    
    return sum(absolute_price_changes) / len(absolute_price_changes)


def extract_date(timestamp: str) -> str:
    return timestamp.split(' ')[0]


def group_prices_by_date(
  timestamp: list[str],
  prices: list[float]      
) -> dict[str, list[float]]:
    daily_prices = {}
    for i, price in enumerate(prices):
        date = extract_date(timestamp[i])
        if date not in daily_prices:
            daily_prices[date] = []

        daily_prices[date].append(price)

    return daily_prices


def calculate_break_even_price(buy_price: float, efficiency: float) -> float:
    if efficiency <= 0 or efficiency > 1:
            raise ValueError("Efficiency must be between 0 (exclusive) and 1 (inclusive)")
    
    return buy_price / efficiency


def find_best_trade(prices: list[float], efficiency: float, trading_cost: float) -> tuple[float, int | None, int | None]:
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("Efficiency must be between 0 (exclusive) and 1 (inclusive)")
    elif trading_cost < 0:
        raise ValueError("Trading cost cannot be negative")
    
    best_profit = 0.0
    best_buy_index = None
    best_sell_index = None

    for buy_index in range(len(prices)):
        for sell_index in range(buy_index + 1, len(prices)):
            profit = (
                efficiency * (prices[sell_index] - trading_cost)
                - (prices[buy_index] - trading_cost)
            )
            if profit > best_profit:
                best_profit = profit
                best_buy_index = buy_index
                best_sell_index = sell_index

    return best_profit, best_buy_index, best_sell_index


def main():
    file_path = get_data_path() / 'dk1_prices_2024_week1.csv'
    print("Starting Power Data Explorer")

    energy_prices = []
    timestamps = []

    with open(file_path, newline='', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        for row in reader:
            price = float(row["DK1_EUR/MWh"].replace(",","."))
            energy_prices.append(price)
            timestamps.append(row["HourDK"])

    negative_hours = count_negative_hours(energy_prices)
    zero_hours = count_zero_hours(energy_prices)

    negative_price_percentage = negative_hours / len(energy_prices) * 100

    lowest_price = min(energy_prices)
    highest_price = max(energy_prices)

    hourly_price_changes = calculate_hourly_changes(energy_prices)

    largest_price_increase = max(hourly_price_changes)
    largest_price_increase_index = hourly_price_changes.index(largest_price_increase)
    largest_price_decrease = min(hourly_price_changes)
    largest_price_decrease_index = hourly_price_changes.index(largest_price_decrease)

    average_absolute_price_change = calculate_average_absolute_price_change(hourly_price_changes)

    daily_prices = group_prices_by_date(timestamps, energy_prices)

    daily_average_prices = {}

    for date, prices in daily_prices.items():
        average = sum(prices) / len(prices)
        daily_average_prices[date] = average

    datetime_timestamps = []
    
    for timestamp in timestamps:
        datetime_timestamps.append(datetime.strptime(timestamp, TIMESTAMP_FORMAT))
    
    hourly_daily_averages = []
    
    for timestamp in timestamps:
        price = daily_average_prices[extract_date(timestamp)]
        hourly_daily_averages.append(price)

    daily_price_range = {}

    for date, prices in daily_prices.items():
        daily_price_range[date] = max(prices) - min(prices)

    largest_daily_price_range_date = max(daily_price_range, key=daily_price_range.get)
    largest_daily_price_range = daily_price_range[largest_daily_price_range_date]

    smallest_daily_price_range_date = min(daily_price_range, key=daily_price_range.get)
    smallest_daily_price_range = daily_price_range[smallest_daily_price_range_date]

    daily_best_trades = {}

    for date, prices in daily_prices.items():
        daily_best_trades[date] = find_best_trade(prices, BATTERY_EFFICIENCY, TRADING_COST)


    real_profit, soc_history, profit_history = simulate_battery(energy_prices)
    print(f'Total profit: {real_profit:.2f} EUR')

    print('Output:')
    print(f'Negative price hours: {negative_hours}')
    print(f'Share of negative hours: {negative_price_percentage:.2f}%')

    print(f'Zero price hours: {zero_hours}')
    print(f'Lowest price: {lowest_price:+.2f} EUR/MWh')
    print(f'Highest price: {highest_price:+.2f} EUR/MWh')

    print(f'Largest price increase: {largest_price_increase:+.2f} EUR/MWh\nFrom: [{timestamps[largest_price_increase_index]}]\nTo: [{timestamps[largest_price_increase_index + 1]}]')
    print(f'Largest price decrease: {largest_price_decrease:+.2f} EUR/MWh\nFrom: [{timestamps[largest_price_decrease_index]}]\nTo: [{timestamps[largest_price_decrease_index + 1]}]')
    print(f'Average absolute price change: {average_absolute_price_change:.2f} EUR/MWh')

    print('Daily average prices:')
    for date, price in daily_average_prices.items():
        print(f'{date}: {price:+.2f} EUR/MWh')

    print(f'Highest average date: {max(daily_average_prices,key=daily_average_prices.get)}')
    print(f'Lowest average date: {min(daily_average_prices,key=daily_average_prices.get)}')

    print(f'Largest daily price range: {largest_daily_price_range_date} ({largest_daily_price_range:.2f} EUR/MWh)')
    print(f'Smallest daily price range: {smallest_daily_price_range_date} ({smallest_daily_price_range:.2f} EUR/MWh)')

    for date, trade in daily_best_trades.items():
        profit, buy_index, sell_index = trade
        print(f'{date}: Profit {profit:.2f} EUR | Buy: {buy_index} | Sell: {sell_index}')

    fig, axs = plt.subplots(2,2, figsize=(15, 10))

    axs[0,0].plot(datetime_timestamps, energy_prices, label = "Hourly price", c = 'b')
    axs[0,0].plot(datetime_timestamps, hourly_daily_averages, 
        linestyle = '--', label = 'Average price by day', linewidth = 2, c = 'r'
    )
    axs[0,0].set_title('Price per hour')
    axs[0,0].xaxis.set_major_locator(mdates.DayLocator())
    axs[0,0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    axs[0,0].set_ylabel('EUR/MWh')
    axs[0,0].set_xlabel('Date')
    axs[0,0].legend()
    axs[0,0].grid(axis = 'y')

    axs[0,1].plot(datetime_timestamps, soc_history, c = 'g')
    axs[0,1].set_title('State of charge')
    axs[0,1].xaxis.set_major_locator(mdates.DayLocator())
    axs[0,1].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    axs[0,1].set_ylabel('SoC %')
    axs[0,1].set_xlabel('Date')
    axs[0,1].set_ylim([0,100])
    axs[0,1].grid(c = 'gray', linestyle = '--')

    axs[1,0].plot(datetime_timestamps, profit_history, c = 'gold')
    axs[1,0].set_title('Profit history')
    axs[1,0].xaxis.set_major_locator(mdates.DayLocator())
    axs[1,0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    axs[1,0].set_ylabel('EUR')
    axs[1,0].set_xlabel('Date')
    axs[1,0].grid()

    axs[1,1].axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()