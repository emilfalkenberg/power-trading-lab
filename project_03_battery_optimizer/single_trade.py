import pandas as pd

def calculate_profit(buy_price, sell_price, energy_bought, efficiency, trading_cost) -> float:
    energy_sold = efficiency * energy_bought
    return (energy_sold * sell_price - energy_bought * buy_price) - (energy_sold + energy_bought) * trading_cost


def find_best_trade(df: pd.DataFrame, energy_bought: float, efficiency: float, trading_cost: float) -> tuple[float, int | None, int | None, int]:
    combinations = 0
    best_profit = 0
    best_buy_hour = None
    best_sell_hour = None

    for buy_index, buy_row in df.iterrows():
        for sell_index, sell_row in df.iterrows():
            if sell_index > buy_index:
                profit = calculate_profit(buy_row["DK1_EUR/MWh"], sell_row["DK1_EUR/MWh"], energy_bought, efficiency, trading_cost)
                combinations += 1
                if profit > best_profit:
                    best_profit = profit
                    best_buy_hour = buy_index
                    best_sell_hour = sell_index

    return best_profit, best_buy_hour, best_sell_hour, combinations