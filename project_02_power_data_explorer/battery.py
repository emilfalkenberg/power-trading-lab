
# Battery constants
BATTERY_EFFICIENCY = 0.85
CAPACITY_MWH = 100
POWER_MW = 25
HOURS = 1
SELF_DISCHARGE_RATE = 0.001
TRADING_COST = 5                            # EUR / MWh

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

def decide_action(price: float) -> str:
    if price < 40:
        return "buy"
    elif price > 75:
        return "sell"
    else:
        return "hold"

def simulate_battery(prices: list[float]) -> tuple[float, list[float], list[float]]:
    total_profit = 0
    current_energy_mwh = 0
    total_energy_bought = 0
    total_energy_sold = 0
    number_of_trades = 0
    soc_history = []
    profit_history = []

    for i, price in enumerate(prices):
        action = decide_action(price)

        if action == "buy":
            energy_change = calculate_max_charge(CAPACITY_MWH, POWER_MW, HOURS, current_energy_mwh)
            total_energy_bought += energy_change
            if energy_change == 0:
                action = "hold"
            elif energy_change > 0:
                number_of_trades += 1
            current_energy_mwh = update_energy_battery(current_energy_mwh, energy_change, CAPACITY_MWH)
            total_profit -= energy_change * ( price + TRADING_COST)
        elif action == "sell":
            energy_change = calculate_max_discharge(POWER_MW, HOURS, current_energy_mwh)
            if energy_change == 0:
                action = "hold"
            elif energy_change > 0:
                number_of_trades += 1
            current_energy_mwh = update_energy_battery(current_energy_mwh, -energy_change, CAPACITY_MWH)
            energy_sold = calculate_sellable_energy(energy_change, BATTERY_EFFICIENCY)
            total_energy_sold += energy_sold
            total_profit += energy_sold * price - (energy_sold * TRADING_COST)


        profit_history.append(total_profit)
        discharge_loss = calculate_hourly_self_discharge(current_energy_mwh, SELF_DISCHARGE_RATE)
        current_energy_mwh = update_energy_battery(current_energy_mwh, discharge_loss, CAPACITY_MWH)
        current_soc = current_energy_mwh / CAPACITY_MWH * 100
        soc_history.append(current_soc)

        print(f'Hour {i:02} | {action.capitalize()} | Price: {price:.2f} | SOC: {current_soc:.2f} %')

    print(f'Remaining state of charge: {current_energy_mwh:.2f} MWh')
    print(f'Total energy bought: {total_energy_bought:.2f} MWh')
    print(f'Total energy sold: {total_energy_sold:.2f} MWh')
    print(f'Total energy loss: {(total_energy_bought - ( total_energy_sold + current_energy_mwh) ):.2f} MWh')
    print(f'Number of trades: {number_of_trades}')

    assert len(profit_history) == len(prices)
    assert len(soc_history) == len(prices)
    
    return total_profit, soc_history, profit_history