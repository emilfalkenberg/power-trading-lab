import pytest
from optimizer import optimize_battery

@pytest.fixture
def battery_result():
    prices = [-50, -40, -30]

    result = optimize_battery(
        prices=prices,
        efficiency=0.85,
        trading_cost=0,
        capacity_mwh=10,
        power_mw=5,
        hours_per_period=1,
    )

    return prices, result

def test_result_length(battery_result):
    prices, result = battery_result

    assert (len(prices) == len(result.charge))
    assert (len(prices) == len(result.discharge))
    assert (len(prices) == len(result.energy_history))
    assert (len(prices) == len(result.profit_history))

def test_negative_prices_profit(battery_result):
    _, result = battery_result

    assert abs(result.total_profit - 122.50) < 1e-6

def test_no_simultaneous_charge_discharge(battery_result):
    _, result = battery_result
    
    for charge, discharge in zip(result.charge, result.discharge):
        assert abs(charge * discharge) < 1e-6

def test_energy_balance(battery_result):
    _, result = battery_result

    calculated = 0

    for charge, discharge, reported in zip(result.charge, result.discharge, result.energy_history):
        calculated += charge - discharge
        assert abs(calculated - reported) < 1e-6
        assert -1e-6 <= calculated <= 10 + 1e-6

def test_no_profitable_trades():
    prices = [50, 50, 50]
    
    result = optimize_battery(
        prices=prices,
        efficiency=0.85,
        trading_cost=5,
        capacity_mwh=10,
        power_mw=5,
        hours_per_period=1,
    )

    assert abs(result.total_profit) < 1e-6

    assert all(
        abs(charge) < 1e-6 and abs(discharge) < 1e-6
        for charge, discharge in zip(result.charge, result.discharge)
    )
    
    

