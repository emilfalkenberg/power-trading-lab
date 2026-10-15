import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime

# global constant
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
BATTERY_EFFICIENCY = 0.85                   
SELF_DISCHARGE_RATE = 0.001                 
TRADING_COST = 5                            # EUR

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


def calculate_average_absolute_price_change(prices: list[float]) -> float:
    if len(prices) == 0:
        raise ValueError('List can\'t be empty')
    
    absolute_price_changes = []

    for price in prices:
        absolute_price_changes.append(abs(price))
    
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
            profit = (efficiency * prices[sell_index] - prices[buy_index]) - trading_cost
            if profit > best_profit:
                best_profit = profit
                best_buy_index = buy_index
                best_sell_index = sell_index

    return best_profit, best_buy_index, best_sell_index

def calculate_max_charge(
    capacity_mwh: float,
    power_mw: float,
    hours: float,
    current_energy_mwh: float
) -> float:
    if current_energy_mwh < 0 or current_energy_mwh > capacity_mwh:
        raise ValueError("Current energy mwh must be between 0 (inclusive) and full capacity (inclusive)")
    elif power_mw < 0 or hours < 0:
        raise ValueError("Hours and Power MW needs to be over 0 (inclusive)")

    remaining_capacity = capacity_mwh - current_energy_mwh
    return min( power_mw * hours , remaining_capacity)


def calculate_max_discharge(
    power_mw: float,
    hours: float,
    current_energy_mwh: float,
) -> float:
    if current_energy_mwh < 0:
        raise ValueError("Current energy mwh must be over 0 (inclusive)")
    elif power_mw < 0 or hours < 0:
        raise ValueError("Hours and Power MW needs to be over 0 (inclusive)")
    
    return min(power_mw * hours, current_energy_mwh)


def calculate_sellable_energy(sellable_energy: float, efficiency: float) -> float:
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("Efficiency must be between 0 (exclusive) and 1 (inclusive)")
    elif sellable_energy < 0:
        raise ValueError("Dischargeble energy needs to be over 0 (inclusive)")

    return sellable_energy * efficiency


def calculate_hourly_self_discharge(
    current_energy_mwh: float, self_discharge_rate: float
) -> float:
    if self_discharge_rate < 0 or self_discharge_rate > 1:
        raise ValueError("Self-discharge rate must be between 0 (inclusive) and 1 (inclusive)")
    elif current_energy_mwh < 0:
        raise ValueError("Current energy MWh needs to be over 0 (inclusive)")
    return - current_energy_mwh * self_discharge_rate


def update_energy_battery(
    current_energy_mwh: float,
    energy_change_mwh: float,
    capacity_mwh: float
) -> float:
    if current_energy_mwh < 0 or current_energy_mwh > capacity_mwh:
        raise ValueError(f'Battery SOC is over capacity ({capacity_mwh}) or below 0')
    battery_mwh = current_energy_mwh + energy_change_mwh
    if battery_mwh < 0:
        raise ValueError(f'Battery can\'t be discharged more than the {current_energy_mwh}')
    elif battery_mwh > capacity_mwh:
        raise ValueError(f'Battery can\'t be charged more than {capacity_mwh}')
    return battery_mwh


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

    capacity_mwh = 100
    power_mw = 25
    current_energy_mwh = 20
    hours = 1
    sell_price = 100
    buy_price = 30

    max_charge = calculate_max_charge(capacity_mwh, power_mw, hours, current_energy_mwh)
    current_energy_mwh = update_energy_battery(current_energy_mwh, max_charge, capacity_mwh)

    max_discharge = calculate_max_discharge(power_mw, hours, current_energy_mwh)
    energy_sold = calculate_sellable_energy(max_discharge, BATTERY_EFFICIENCY)
    current_energy_mwh = update_energy_battery(current_energy_mwh, -max_discharge, capacity_mwh)
    state_of_charge = current_energy_mwh/capacity_mwh * 100
    purchase_cost = buy_price * max_charge
    sales_revenue = sell_price * energy_sold
    profit = sales_revenue - purchase_cost

    action_prices = [30, 35, 60, 100, 80]
    actions = ["buy", "buy", "hold", "sell", "sell"]

    total_profit = 0
    capacity_mwh = 100
    power_mw = 25
    current_energy_mwh = 0
    hours = 1

    for i, price in enumerate(action_prices):
        if actions[i] == "buy":
            energy_change = calculate_max_charge(capacity_mwh, power_mw, hours, current_energy_mwh)
            current_energy_mwh = update_energy_battery(current_energy_mwh, energy_change, capacity_mwh)
            total_profit = total_profit - energy_change * price
        elif actions[i] == "sell":
            energy_change = calculate_max_discharge(power_mw, hours, current_energy_mwh)
            current_energy_mwh = update_energy_battery(current_energy_mwh, -energy_change, capacity_mwh)
            energy_sold = calculate_sellable_energy(energy_change, BATTERY_EFFICIENCY)
            total_profit = total_profit + energy_sold * price
        elif actions[i] == "hold":
            pass

        discharge_loss = calculate_hourly_self_discharge(current_energy_mwh, SELF_DISCHARGE_RATE)
        current_energy_mwh = update_energy_battery(current_energy_mwh, discharge_loss, capacity_mwh)
        print(f'Hour {i:02} | {actions[i].capitalize()} | Price: {price} | SOC: {(current_energy_mwh / capacity_mwh * 100):.2f} %')

    
    print(f'Total profit: {total_profit} EUR')


    print(f'SOC: {state_of_charge} %')
    print(f'Purchase cost: {purchase_cost} EUR')
    print(f'Sales revenue: {sales_revenue} EUR')
    print(f'Profit: {profit} EUR')

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

    plt.plot(datetime_timestamps, energy_prices, label = "Hourly price", c = 'b')
    plt.plot(datetime_timestamps, hourly_daily_averages, 
        linestyle = '--', label = 'Average price by day', linewidth = 2, c = 'r'
    )
    plt.title('Pris pr time')
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    plt.ylabel('EUR/MWh')
    plt.legend()
    plt.grid(axis= 'y')
    plt.show()

assert count_negative_hours([10, -5, 0, -2, 20]) == 2
assert calculate_hourly_changes([20, 35, 10, 50]) == [15, -25, 40]

assert find_best_trade([40, 100], 0.85, 5) == (40.0, 0, 1)

assert find_best_trade([40, 50], 0.85, 5) == (0.0, None, None)

assert find_best_trade([30, 90], 1.0, 0) == (60.0, 0, 1)

assert calculate_max_charge(100, 25, 2, 70) == 30
assert calculate_max_charge(100, 25, 2, 20) == 50
assert calculate_max_charge(100, 25, 2, 100) == 0

assert calculate_max_discharge(25, 2, 40) == 40
assert calculate_max_discharge(25, 1, 70) == 25
assert calculate_max_discharge(25, 2, 0) == 0

if __name__ == "__main__":
    main()