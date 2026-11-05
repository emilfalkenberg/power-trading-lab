import pandas as pd

def validate_market_data(df: pd.DataFrame) -> None:
    
    # Check for dublets
    if df["HourUTC"].duplicated().sum() > 0:
        raise ValueError("Duplicate UTC timestamps found")
    
    # Check if dates are correct
    first_hour = df["HourUTC"].min()
    last_hour = df["HourUTC"].max()
    
    expected_hours = pd.date_range(
        start=first_hour,
        end=last_hour,
        freq="h"
    ) 
    
    missing_hours = expected_hours.difference(pd.DatetimeIndex(df["HourUTC"]))
    
    if not missing_hours.empty:
        raise ValueError(f"Missing {len(missing_hours)} hourly timestamps")
    
    # Check 1 hour interval in dataFrame
    time_steps = df["HourUTC"].diff().dropna()
    if not (time_steps == pd.Timedelta(hours=1)).all():
        raise ValueError("Expected consecutive hourly timestamps")

    # Check for NaN values in prices
    if df["DK1_EUR/MWh"].isna().any():
        raise ValueError("Missing electricity prices: at least one value is NaN")