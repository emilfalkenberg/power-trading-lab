import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from single_trade import find_best_trade
from optimizer import optimize_battery
from validation import validate_market_data

def get_data_path():
    script_dir = Path(__file__).parent.parent

    return script_dir / 'data'


def main():
    file_path = get_data_path() / 'dk1_prices_2024_week1.csv'
    print("Starting Battery Optimizer")

    df = pd.read_csv(file_path, sep=";", decimal=",")
    df["HourDK"] = pd.to_datetime(df["HourDK"])
    df["DK1_EUR/MWh"] = pd.to_numeric(df["DK1_EUR/MWh"])
    df["HourUTC"] = pd.to_datetime(df["HourUTC"], utc=True)

    # Validate market data before optimization
    validate_market_data(df)
    
    df_grouped_by_date = df["DK1_EUR/MWh"].groupby(df["HourDK"].dt.date)

    daily_df = df_grouped_by_date.agg(
        Avg="mean",
        Min="min",
        Max="max",
        Std="std"
    )

    print(daily_df)

    profit, buy_hour, sell_hour, combinations = find_best_trade(df, 10, 0.85, 5)
    print(f'Number of possible trades: {combinations}')
    print(f'Best trade: Buy hour {buy_hour} | Sell hour {sell_hour} | Profit: {profit:+.2f}')

    prices_list = df["DK1_EUR/MWh"].tolist()
    result = optimize_battery(
        prices=prices_list,
        efficiency=0.85,
        trading_cost=5,
        capacity_mwh=100,
        power_mw=25,
        hours_per_period=1,
    )

    df["Charge_MWh"] = result.charge
    df["Discharge_MWh"] = result.discharge
    df["Stored_Energy_MWh"] = result.energy_history
    df["Profit_EUR"] = result.profit_history
    df["Cumulative_Profit_EUR"] = df["Profit_EUR"].cumsum()
    print(f'Total profit: {result.total_profit:.2f} EUR')

    fig, axs = plt.subplots(2,2, figsize=(12, 8), sharex=True)
    axs[0,0].plot(df["HourDK"], df["DK1_EUR/MWh"])
    axs[0,0].set_title("DK1 electricity price")
    axs[0,0].set_ylabel("Price [EUR/MWh]")
    axs[0,0].grid(axis = 'y')

    axs[0,1].plot(df["HourDK"], df["Charge_MWh"], c = "g", label = "Charging")
    axs[0,1].plot(df["HourDK"], -df["Discharge_MWh"], c = "r", label = "Discharging")
    axs[0,1].set_title("Charging and discharging energy")
    axs[0,1].set_ylabel("Energy [MWh]")
    axs[0,1].grid(axis = 'y')
    axs[0,1].legend()

    axs[1,0].plot(df["HourDK"], df["Stored_Energy_MWh"])
    axs[1,0].set_title("Stored energy at end of period")
    axs[1,0].set_ylabel("Stored energy [MWh]")
    axs[1,0].set_xlabel("Delivery period start")
    axs[1,0].grid(axis = 'y')

    axs[1,1].plot(df["HourDK"], df["Cumulative_Profit_EUR"])
    axs[1,1].set_title("Cumulative Profit")
    axs[1,1].set_ylabel("Profit [EUR]")
    axs[1,1].grid(axis = 'y')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()