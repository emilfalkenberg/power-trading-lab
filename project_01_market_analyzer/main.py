energy_prices = [32.14, 28.91, 27.45, 25.80, 24.72, 29.10, 41.35, 58.20, 71.44, 67.91, 54.30, 46.82, 39.17, 35.60, 31.22, 33.85, 48.76, 76.30, 91.42, 84.15, 65.73, 52.40, 43.18 ,36.55]

total_price = sum(energy_prices)
average_price = total_price / len(energy_prices)
highest_price = max(energy_prices)
lowest_price = min(energy_prices)
price_range = highest_price - lowest_price
expensive_hours = {}
cheap_hours = {}
peak_hours = energy_prices[8:20]
peak_average_price = sum(peak_hours) / len(peak_hours)
off_peak_hours = energy_prices[:8] + energy_prices[20:]
off_peak_average_price = sum(off_peak_hours) / len(off_peak_hours)
peak_premium = peak_average_price - off_peak_average_price



for i, price in enumerate(energy_prices):
    if price > average_price:
        expensive_hours[i] = price
    elif price < average_price:
        cheap_hours[i] = price


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