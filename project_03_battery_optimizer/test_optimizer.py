from optimizer import optimize_battery

prices = [-50, -40, -30]

result = optimize_battery(
    prices,
    efficiency=0.85,
    trading_cost=0,
    capacity_mwh=10,
    power_mw=5,
    hours_per_period=1,
)

assert (len(prices) == len(result.charge))
assert (len(prices) == len(result.discharge))
assert (len(prices) == len(result.energy_history))
assert (len(prices) == len(result.profit_history))
assert (result)