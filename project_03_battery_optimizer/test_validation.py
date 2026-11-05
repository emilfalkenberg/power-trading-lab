import pandas as pd
import pytest
from validation import validate_market_data

# Create test data
@pytest.fixture
def valid_market_data():
    return pd.DataFrame({
        "HourUTC": pd.date_range(
            start="2024-01-01",
            periods=3,
            freq="h",
            tz="UTC"
        ),
        "DK1_EUR/MWh": [40, 50, 60]
    })

def test_missing_price(valid_market_data):
    # Introduce a missing price
    df_copy = valid_market_data.copy()

    df_copy.loc[1,"DK1_EUR/MWh"] = float("nan")

    # Verify that validation rejects the data
    with pytest.raises(ValueError, match="Missing electricity prices"):
        validate_market_data(df_copy)

def test_duplicate_timestamp(valid_market_data):
    # Introduce a duplicate
    df_copy = valid_market_data.copy()
    
    df_copy.loc[2,"HourUTC"] = df_copy.loc[0,"HourUTC"]
    
    # Verify that validation rejects the data
    with pytest.raises(ValueError, match="Duplicate UTC timestamps found"):
        validate_market_data(df_copy)