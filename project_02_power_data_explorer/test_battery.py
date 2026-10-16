from battery import simulate_battery

test_prices = [30, 100]
test_profit, test_soc, test_profit_history = simulate_battery(test_prices)

print(f"Test profit: {test_profit:.2f} EUR")

assert abs(test_profit - 1141.73) < 0.01
assert len(test_soc) == len(test_prices)
assert len(test_profit_history) == len(test_prices)
assert abs(test_soc[-1]) < 0.001


# Yderlighedstest

# 1
test_prices = [50, 60, 70]
test_profit, test_soc, test_profit_history = simulate_battery(test_prices)

print(f"Test profit: {test_profit:.2f} EUR")

assert abs(test_profit) < 0.01
assert abs(all(test_soc)) < 0.01
assert abs(all(test_profit_history)) < 0.01
assert len(test_soc) == len(test_prices)
assert len(test_profit_history) == len(test_prices)


# 2
test_prices = [100, 120, 90]
test_profit, test_soc, test_profit_history = simulate_battery(test_prices)

print(f"Test profit: {test_profit:.2f} EUR")

assert abs(test_profit) < 0.01
assert all(abs(soc) < 0.01 for soc in test_soc)
assert all(abs(profit) < 0.01 for profit in test_profit_history)
assert len(test_soc) == len(test_prices)
assert len(test_profit_history) == len(test_prices)