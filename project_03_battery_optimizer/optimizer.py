from scipy.optimize import LinearConstraint, Bounds, milp
from typing import NamedTuple

class BatteryResult(NamedTuple):
    total_profit: float
    profit_history: list[float]
    energy_history: list[float]
    charge: list[float]
    discharge: list[float]


def optimize_battery(
    prices: list[float],
    efficiency: float,
    trading_cost: float,
    capacity_mwh: float,
    power_mw: float,
    hours_per_period: float,
) -> BatteryResult:
    n = len(prices)
    if n < 1: raise ValueError('List of prices can\'t be empty')
    if not (0 < efficiency <= 1): raise ValueError("Efficiency must be between 0 (exc.) and 1 (inc.)")
    if trading_cost < 0: raise ValueError("Trading cost must be non-negative")
    if hours_per_period <= 0: raise ValueError("Hours per period must be positive")
    if capacity_mwh <= 0 or power_mw <= 0: raise ValueError("Capacity and Power must be positive")

    buying_coefficients = [price + trading_cost for price in prices]
    sell_coefficients = [- efficiency * (price - trading_cost) for price in prices]
    max_energy_mwh = power_mw * hours_per_period
    c = buying_coefficients + sell_coefficients + [0] * n
    lb = [0] * (3 * n)
    ub = [max_energy_mwh] * (2 * n) + [1] * n
    bounds = Bounds(lb,ub)
    integrality = [0] * (2 * n) + [1] * n
    A_ub = []
    b_ub = []

    for t in range(n):
        charge_row = [0] * (3 * n)
        charge_row[t] = 1
        charge_row[t + 2 * n] = max_energy_mwh

        discharge_row = [0] * (3 * n)
        discharge_row[t+n] = 1
        discharge_row[t+2*n] = -max_energy_mwh

        row = [0] * (3 * n)

        for i in range(t + 1):
            row[i] = 1
            row[i + n] = -1

        A_ub.append(charge_row)
        b_ub.append(max_energy_mwh)
        A_ub.append(discharge_row)
        b_ub.append(0)
        A_ub.append(row)
        b_ub.append(capacity_mwh)
        negative_row = [-value for value in row]
        A_ub.append(negative_row)
        b_ub.append(0)

    A_eq = [[1] * n + [-1] * n + [0] * n]
    b_eq = [0]  

    inequality_constraints = LinearConstraint(A_ub, -float("inf"),b_ub)

    equality_constraints = LinearConstraint(A_eq, b_eq, b_eq)

    result = milp(
        c=c,
        integrality=integrality,
        bounds=bounds,
        constraints = [inequality_constraints, equality_constraints]
    )

    if result.success:
        charge = result.x[:n].tolist()
        discharge = result.x[n:2*n].tolist()
        z = result.x[2*n:].tolist()

        current_energy_mwh = 0
        energy_history = []
        profit_history = []

        for t in range(n):
            energy_change = charge[t] - discharge[t]
            current_energy_mwh += energy_change
            energy_history.append(float(current_energy_mwh))
            period_profit = (
                discharge[t] * efficiency * (prices[t] - trading_cost) 
                - charge[t] * (prices[t] + trading_cost)
            )
            profit_history.append(float(period_profit))

        total_profit = sum(profit_history)

        assert abs(sum(profit_history) - (-result.fun)) < 1e-6
        assert abs(energy_history[-1]) < 1e-6
        assert all(
            -1e-6 <= energy <= capacity_mwh + 1e-6
            for energy in energy_history
        )
        assert all(
            -1e-6 <= energy <= max_energy_mwh + 1e-6
            for energy in charge
        )
        assert all(
                -1e-6 <= energy <= max_energy_mwh + 1e-6
                for energy in discharge
        )

        return BatteryResult(
            total_profit=total_profit,
            profit_history=profit_history,
            energy_history=energy_history,
            charge=charge,
            discharge=discharge,
        )
    else:
        raise RuntimeError(f"Optimization failed: {result.message}")




""" prices = [-50,-40,-30]

result = optimize_battery(
    prices=prices,
    efficiency=0.85,
    trading_cost=0,
    capacity_mwh=10,
    power_mw=5,
    hours_per_period=1,
)

print(result.charge)
print(result.discharge)
print(result.energy_history)
print(result.total_profit) """