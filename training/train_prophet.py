import pandas as pd
import numpy as np
from prophet import Prophet
import json
import sys
import os
import sqlite3
import pickle
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def train_prophet():
    """Train Prophet model and convert irradiance to energy (Fix 4)"""
    
    # Use absolute path for data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data')
    weather_path = os.path.join(data_dir, 'weather_data.csv')
    
    if not os.path.exists(weather_path):
        print(f"Weather data not found at {weather_path}, creating sample data...")
        create_sample_weather_data(data_dir)
        weather_path = os.path.join(data_dir, 'weather_data.csv')
    
    df = pd.read_csv(weather_path)

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

    result = forecast[['ds','yhat']].copy()
    
    # Fix 4: Convert irradiance to energy using panel parameters
    result.loc[:, 'yhat'] = result['yhat'].apply(
        lambda irr: max(0, panel_count * panel_power / 1000 * (irr / 1000) * 5.5 * 0.8)
    )
    
    solar_forecast_path = os.path.join(data_dir, 'solar_forecast.csv')
    result.to_csv(solar_forecast_path, index=False)

    # Wind speed forecast
    wind = df[['date','wind_speed']]
    wind.columns = ['ds','y']

    model_wind = Prophet()
    model_wind.fit(wind)

    forecast_wind = model_wind.predict(future)
    result_wind = forecast_wind[['ds','yhat']].copy()
    
    # Fix 4: Convert wind speed to energy (using the same logic as main.py)
    result_wind.loc[:, 'yhat'] = result_wind['yhat'].apply(
        lambda speed: max(0, calculate_wind_energy(speed))
    )
    
    wind_forecast_path = os.path.join(data_dir, 'wind_forecast.csv')
    result_wind.to_csv(wind_forecast_path, index=False)
    
    # Save trained models for persistence
    save_trained_models(model, model_wind, data_dir)
    
    print(f"Training completed. Models saved to {data_dir}")
    return True


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

def create_sample_weather_data(data_dir):
    """Create sample weather data for training if none exists"""
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate 90 days of historical weather data
    dates = []
    solar_radiation = []
    wind_speed = []
    temperature = []
    
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(90):
        current_date = base_date + timedelta(days=i)
        dates.append(current_date.strftime('%Y-%m-%d'))
        
        # Simulate realistic weather patterns
        day_of_year = current_date.timetuple().tm_yday
        seasonal_factor = 0.7 + 0.3 * np.sin(2 * np.pi * day_of_year / 365)
        
        # Solar radiation with daily and seasonal variation
        daily_solar = 5.0 * seasonal_factor * (0.8 + 0.2 * np.random.random())
        solar_radiation.append(round(daily_solar, 2))
        
        # Wind speed with more variability
        daily_wind = 3.5 * (0.6 + 0.4 * np.random.random())
        wind_speed.append(round(daily_wind, 2))
        
        # Temperature
        daily_temp = 20 + 10 * seasonal_factor + np.random.normal(0, 2)
        temperature.append(round(daily_temp, 2))
    
    # Create DataFrame
    weather_df = pd.DataFrame({
        'date': dates,
        'solar_radiation': solar_radiation,
        'wind_speed': wind_speed,
        'temperature': temperature
    })
    
    weather_path = os.path.join(data_dir, 'weather_data.csv')
    weather_df.to_csv(weather_path, index=False)
    print(f"Created sample weather data with {len(weather_df)} records at {weather_path}")
    
    return weather_df

def save_trained_models(solar_model, wind_model, data_dir):
    """Save trained Prophet models to disk"""
    os.makedirs(data_dir, exist_ok=True)
    
    solar_model_path = os.path.join(data_dir, 'solar_prophet_model.pkl')
    wind_model_path = os.path.join(data_dir, 'wind_prophet_model.pkl')
    
    with open(solar_model_path, 'wb') as f:
        pickle.dump(solar_model, f)
    
    with open(wind_model_path, 'wb') as f:
        pickle.dump(wind_model, f)
    
    print(f"Saved trained models: {solar_model_path}, {wind_model_path}")

def load_trained_models(data_dir):
    """Load trained Prophet models from disk"""
    solar_model_path = os.path.join(data_dir, 'solar_prophet_model.pkl')
    wind_model_path = os.path.join(data_dir, 'wind_prophet_model.pkl')
    
    if os.path.exists(solar_model_path) and os.path.exists(wind_model_path):
        with open(solar_model_path, 'rb') as f:
            solar_model = pickle.load(f)
        
        with open(wind_model_path, 'rb') as f:
            wind_model = pickle.load(f)
        
        print(f"Loaded trained models from {data_dir}")
        return solar_model, wind_model
    else:
        print("No trained models found")
        return None, None
