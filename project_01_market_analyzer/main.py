
# Funktioner
def calculate_price_range(prices: list[float]) -> float:
    if len(prices) == 0:
        raise ValueError('List can\'t be empty')
    
    return max(prices) - min(prices)
    
def calculate_average_price(prices: list[float]) -> float:
    if len(prices) == 0:
        raise ValueError('List can\'t be empty')
    
    return sum(prices) / len(prices)

def calculate_standard_deviation_price(prices: list[float]) -> float:
    n = len(prices)
    
    if n == 0:
        raise ValueError('List can\'t be empty')
    variance = 0
    average_price = calculate_average_price(prices)

    for price in prices:
        variance += (price - average_price)**2 / n

    return variance**0.5

def calculate_hourly_changes(prices: list[float]) -> list[float]:
    n = len(prices)
    if n <= 1: 
        raise ValueError("At least two prices are required")

    price_changes = []
    for i in range(n - 1):
        price_changes.append(prices[i+1] - prices[i])
    
    return price_changes

def main():
    print("Starting Power Trading Lab")

    # Data
    energy_prices = [32.14, 28.91, 27.45, 25.80, 24.72, 29.10, 41.35, 58.20, 71.44, 67.91, 54.30, 46.82, 39.17, 35.60, 31.22, 33.85, 48.76, 76.30, 91.42, 84.15, 65.73, 52.40, 43.18, 36.55]
    
    # Beregniner
    price_range = calculate_price_range(energy_prices)
    average_price = calculate_average_price(energy_prices)
    standard_deviation = calculate_standard_deviation_price(energy_prices)
    highest_price = max(energy_prices)
    lowest_price = min(energy_prices)
    expensive_hours = {}
    cheap_hours = {}
    peak_hours = energy_prices[8:20]
    peak_average_price = calculate_average_price(peak_hours)
    off_peak_hours = energy_prices[:8] + energy_prices[20:]
    off_peak_average_price = calculate_average_price(off_peak_hours)
    peak_premium = peak_average_price - off_peak_average_price
    price_changes = calculate_hourly_changes(energy_prices)

    for i, price in enumerate(energy_prices):
        if price > average_price:
            expensive_hours[i] = price
        elif price < average_price:
            cheap_hours[i] = price

    largest_increase = max(price_changes)
    largest_increase_index = price_changes.index(largest_increase)
    largest_decrease = min(price_changes)
    largest_decrease_index = price_changes.index(largest_decrease)

    # Output
    print(
        f"---DK1 DAY-AHEAD MARKET SUMMARY---\n\n"
        f"Average price: {average_price:.2f} EUR/MWh\n"
        f"Highest price: {highest_price:.2f} EUR/MWh at hour {energy_prices.index(highest_price):02}\n"
        f"Lowest price: {lowest_price:.2f} EUR/MWh at hour {energy_prices.index(lowest_price):02}\n"
        f"Price range: {price_range:.2f} EUR/MWh"
    )

    print("\n---EXPENSIVE HOURS---")
    for hour, price in expensive_hours.items():
        print(f"Hour {hour:02}: {price:.2f} EUR/MWh")

    print("\n---CHEAP HOURS---")
    for hour, price in cheap_hours.items():
        print(f"Hour {hour:02}: {price:.2f} EUR/MWh")

    print(
        f"\n---PEAK ANALYSIS---\n\n"
        f"Peak average: {peak_average_price:.2f} EUR/MWh\n"
        f"Off peak average: {off_peak_average_price:.2f} EUR/MWh\n"
        f"Peak premium: {peak_premium:.2f} EUR/MWh"
    )

    print("\n---HOURLY PRICE CHANGES---")
    for hour, price in enumerate(price_changes):
        print(f"Hour {hour:02} -> {hour+1:02} : {price:+.2f} EUR/MWh")

    print(
        f"Largest increase: {largest_increase:+.2f} EUR/MWh from hour {largest_increase_index:02} to {largest_increase_index+1:02}\n"
        f"Largest decrease: {largest_decrease:+.2f} EUR/MWh from hour {largest_decrease_index:02} to {largest_decrease_index+1:02}\n"
    )

    print(
        f"\n---PRICE VOLATILITY---\n\n"
        f"Standard deviation: {standard_deviation:.2f} EUR/MWh\n"
    )

assert calculate_hourly_changes([10, 10, 10]) == [0, 0]
assert calculate_price_range([10, 20, 30]) == 20
assert calculate_average_price([20,40,60]) == 40
assert calculate_standard_deviation_price([5,5,5]) == 0

if __name__ == "__main__":
    main()

