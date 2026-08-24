import pandas as pd
from prophet import Prophet
import json
import sys
import os
import sqlite3

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def train_prophet():
    """Train Prophet model and convert irradiance to energy (Fix 4)"""
    
    df = pd.read_csv('data/weather_data.csv')

    # Get active configuration for panel parameters (Fix 4) - avoid circular import
    panel_count, panel_power = get_panel_config()
    print(f"DEBUG: Using panel_count={panel_count}, panel_power={panel_power}")

    # Solar radiation forecast
    solar = df[['date','solar_radiation']]
    solar.columns = ['ds','y']

    model = Prophet()
    model.fit(solar)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    result = forecast[['ds','yhat']]
    
    # Fix 4: Convert irradiance to energy using panel parameters
    result['yhat'] = result['yhat'].apply(
        lambda irr: max(0, panel_count * panel_power / 1000 * (irr / 1000) * 5.5 * 0.8)
    )
    
    result.to_csv('data/solar_forecast.csv', index=False)

    # Wind speed forecast
    wind = df[['date','wind_speed']]
    wind.columns = ['ds','y']

    model_wind = Prophet()
    model_wind.fit(wind)

    forecast_wind = model_wind.predict(future)
    result_wind = forecast_wind[['ds','yhat']]
    
    # Fix 4: Convert wind speed to energy (using the same logic as main.py)
    result_wind['yhat'] = result_wind['yhat'].apply(
        lambda speed: max(0, calculate_wind_energy(speed))
    )
    
    result_wind.to_csv('data/wind_forecast.csv', index=False)


def get_panel_config():
    """Get panel configuration from database without circular import"""
    try:
        # Direct database access to avoid circular import
        db_path = os.path.join(os.path.dirname(__file__), '..', 'ecogrid.db')
        if not os.path.exists(db_path):
            print("DEBUG: Database not found, using defaults")
            return 20, 400
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get most recent active configuration
        cursor.execute("""
            SELECT config_data FROM system_configuration 
            WHERE is_active = 1 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            config = json.loads(result[0])
            solar_config = config.get('solar', {})
            panel_count = int(solar_config.get('panel_count', 20))
            panel_power = float(solar_config.get('panel_power', 400))
            print(f"DEBUG: Loaded from DB - panel_count={panel_count}, panel_power={panel_power}")
            return panel_count, panel_power
        else:
            print("DEBUG: No active config found, using defaults")
            return 20, 400
            
    except Exception as e:
        print(f"DEBUG: Error getting panel config: {e}, using defaults")
        return 20, 400


def calculate_wind_energy(wind_speed):
    """Calculate wind energy from speed (simplified version for Fix 4)"""
    # Use turbine parameters from config if available, otherwise use defaults
    turbine_count = 2
    turbine_rated_power = 5000
    turbine_efficiency = 0.35
    cut_in_speed = 3
    cut_out_speed = 25
    
    if wind_speed >= cut_in_speed and wind_speed <= cut_out_speed:
        return (turbine_count * turbine_rated_power * turbine_efficiency * 
                (wind_speed / 12) ** 3) / 1000  # kWh
    else:
        return 0
