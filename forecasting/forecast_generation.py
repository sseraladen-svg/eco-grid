import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import pickle

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from training.train_prophet import load_trained_models, train_prophet

def to_float(value, default=0.0):
    try:
        if value == "" or value is None:
            return default
        return float(value)
    except:
        return default


def generate_forecast(config):
    """
    Generate 30-day energy forecast using Prophet AI models
    """
    print("Generating 30-day energy forecast using Prophet AI...")
    
    # Get user configuration
    solar = config.get("solar", {})
    wind = config.get("wind", {})
    battery = config.get("battery", {})
    consumption = config.get("consumption", {})
    location = config.get("location", {})
    
    # Get data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Try to load trained Prophet models
    solar_model, wind_model = load_trained_models(data_dir)
    
    if solar_model is None or wind_model is None:
        print("No trained models found, training Prophet models...")
        try:
            train_prophet()
            solar_model, wind_model = load_trained_models(data_dir)
            if solar_model is None or wind_model is None:
                print("Model training failed, using fallback simulation")
                return generate_simulation_forecast(config, data_dir)
        except Exception as e:
            print(f"Error training models: {e}, using fallback simulation")
            return generate_simulation_forecast(config, data_dir)

    # Generate forecast using Prophet models
    return generate_prophet_forecast(solar_model, wind_model, config, data_dir)

def generate_prophet_forecast(solar_model, wind_model, config, data_dir):
    """Generate forecast using trained Prophet models"""
    print("Generating forecast using trained Prophet models...")
    
    # Get user configuration
    solar = config.get("solar", {})
    wind = config.get("wind", {})
    battery = config.get("battery", {})
    consumption = config.get("consumption", {})
    
    # Extract parameters
    panel_power = to_float(solar.get("panel_power", 400))
    panel_count = to_float(solar.get("panel_count", 10))
    panel_efficiency = to_float(solar.get("panel_efficiency", 20)) / 100
    system_loss = to_float(solar.get("system_loss", 15)) / 100
    
    turbine_power = to_float(wind.get("rated_power", 5000))
    turbine_count = to_float(wind.get("turbine_count", 2))
    turbine_efficiency = to_float(wind.get("turbine_efficiency", 35)) / 100
    cut_in_speed = to_float(wind.get("cut_in_speed", 3))
    cut_out_speed = to_float(wind.get("cut_out_speed", 25))
    
    battery_capacity = to_float(battery.get("battery_capacity", 13.5))
    charge_efficiency = to_float(battery.get("charge_efficiency", 95)) / 100
    discharge_efficiency = to_float(battery.get("discharge_efficiency", 95)) / 100
    
    daily_demand = to_float(consumption.get("daily_energy_usage", 30))
    load_profile_type = consumption.get("load_profile_type", "residential")
    
    # Create future dataframe for 30 days
    future_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
    future_df = pd.DataFrame({'ds': future_dates})
    
    # Generate predictions using Prophet models
    solar_forecast = solar_model.predict(future_df)
    wind_forecast = wind_model.predict(future_df)
    
    # Generate forecast data
    forecast_data = []
    for i in range(30):
        current_date = future_dates[i]
        
        # Get Prophet predictions
        solar_pred = max(0, float(solar_forecast.iloc[i]['yhat']))
        wind_pred = max(0, float(wind_forecast.iloc[i]['yhat']))
        
        # Get prediction intervals for confidence calculation
        solar_lower = float(solar_forecast.iloc[i]['yhat_lower'])
        solar_upper = float(solar_forecast.iloc[i]['yhat_upper'])
        wind_lower = float(wind_forecast.iloc[i]['yhat_lower'])
        wind_upper = float(wind_forecast.iloc[i]['yhat_upper'])
        
        # Convert predictions to energy using user configuration
        solar_energy = (
            solar_pred *  # kWh/m²/day
            panel_power *  # Watts per panel
            panel_count *  # Number of panels
            panel_efficiency *  # Panel efficiency
            (1 - system_loss) *  # System losses
            5.5 / 1000  # Peak sun hours and convert to kWh
        )
        
        # Wind energy calculation
        # wind_pred is wind speed in m/s from Prophet model
        if wind_pred < cut_in_speed or wind_pred > cut_out_speed:
            wind_energy = 0
        else:
            wind_energy = (
                turbine_count * turbine_power * turbine_efficiency * 
                (wind_pred / 12) ** 3) / 1000  # kWh
        
        total_generation = solar_energy + wind_energy
        
        # Calculate demand pattern
        hourly_demand = daily_demand / 24 * (0.8 + 0.4 * np.sin(2 * np.pi * i / 24))
        
        # Battery calculation
        surplus = total_generation - hourly_demand
        if surplus > 0:
            charge_amount = min(surplus * charge_efficiency, battery_capacity * 0.2)
            battery_storage = charge_amount
        else:
            discharge_amount = min(abs(surplus) / discharge_efficiency, battery_capacity * 0.2)
            battery_storage = -discharge_amount
        
        # Calculate confidence based on prediction intervals
        solar_range = solar_upper - solar_lower
        wind_range = wind_upper - wind_lower
        avg_range = (solar_range + wind_range) / 2
        confidence = max(50, min(95, 100 - (avg_range / (solar_pred + wind_pred + 1) * 100)))
        
        forecast_data.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "solar_energy": round(solar_energy, 2),
            "wind_energy": round(wind_energy, 2),
            "total_generation": round(total_generation, 2),
            "demand": round(hourly_demand, 2),
            "battery_storage": round(abs(battery_storage), 2),
            "energy_export": round(max(0, surplus), 2),
            "energy_import": round(max(0, -surplus), 2),
            "confidence": round(confidence, 1),
            "solar_prediction_interval": {
                "lower": round(solar_lower, 2),
                "upper": round(solar_upper, 2)
            },
            "wind_prediction_interval": {
                "lower": round(wind_lower, 2),
                "upper": round(wind_upper, 2)
            }
        })
    
    # Save to CSV
    result = pd.DataFrame(forecast_data)
    forecast_path = os.path.join(data_dir, 'forecast_output.csv')
    result.to_csv(forecast_path, index=False)
    
    print(f"Generated Prophet forecast with {len(result)} records")
    print(f"Total solar generation: {result['solar_energy'].sum():.2f} kWh")
    print(f"Total wind generation: {result['wind_energy'].sum():.2f} kWh")
    print(f"Average confidence: {result['confidence'].mean():.1f}%")
    
    return result

def generate_simulation_forecast(config, data_dir):
    """Fallback simulation forecast when Prophet models are not available"""
    print("Using simulation forecast as fallback...")
    
    # Get user configuration
    solar = config.get("solar", {})
    wind = config.get("wind", {})
    battery = config.get("battery", {})
    consumption = config.get("consumption", {})
    
    # Extract parameters
    panel_power = to_float(solar.get("panel_power", 400))
    panel_count = to_float(solar.get("panel_count", 10))
    panel_efficiency = to_float(solar.get("panel_efficiency", 20)) / 100
    system_loss = to_float(solar.get("system_loss", 15)) / 100
    
    turbine_power = to_float(wind.get("rated_power", 5000))
    turbine_count = to_float(wind.get("turbine_count", 2))
    turbine_efficiency = to_float(wind.get("turbine_efficiency", 35)) / 100
    cut_in_speed = to_float(wind.get("cut_in_speed", 3))
    cut_out_speed = to_float(wind.get("cut_out_speed", 25))
    
    battery_capacity = to_float(battery.get("battery_capacity", 13.5))
    charge_efficiency = to_float(battery.get("charge_efficiency", 95)) / 100
    discharge_efficiency = to_float(battery.get("discharge_efficiency", 95)) / 100
    
    daily_demand = to_float(consumption.get("daily_energy_usage", 30))
    load_profile_type = consumption.get("load_profile_type", "residential")
    
    # Generate 30-day forecast data
    forecast_data = []
    base_date = datetime.now()
    
    for i in range(30):
        current_date = base_date + timedelta(days=i)
        
        # Simulate weather patterns
        day_of_year = current_date.timetuple().tm_yday
        solar_seasonal = 0.7 + 0.3 * np.sin(2 * np.pi * day_of_year / 365)
        
        # Simulated weather
        solar_radiation = 5.0 * solar_seasonal * (0.8 + 0.2 * np.random.random())
        wind_speed = 3.5 * (0.7 + 0.3 * np.random.random())
        
        # Calculate energy generation
        solar_energy = (
            solar_radiation * panel_power * panel_count * panel_efficiency *
            (1 - system_loss) * 5.5 / 1000
        )
        
        if wind_speed < cut_in_speed or wind_speed > cut_out_speed:
            wind_energy = 0
        else:
            wind_energy = (
                turbine_count * turbine_power * turbine_efficiency * 
                (wind_speed / 12) ** 3) / 1000  # kWh
        
        total_generation = solar_energy + wind_energy
        
        # Load profile
        if load_profile_type == "residential":
            hourly_demand = daily_demand / 24 * (0.8 + 0.4 * np.sin(2 * np.pi * i / 24))
        elif load_profile_type == "commercial":
            hourly_demand = daily_demand / 24 * (0.6 + 0.8 * np.sin(2 * np.pi * (i - 6) / 24))
        else:
            hourly_demand = daily_demand / 24
        
        # Battery calculation
        surplus = total_generation - hourly_demand
        if surplus > 0:
            charge_amount = min(surplus * charge_efficiency, battery_capacity * 0.2)
            battery_storage = charge_amount
        else:
            discharge_amount = min(abs(surplus) / discharge_efficiency, battery_capacity * 0.2)
            battery_storage = -discharge_amount
        
        forecast_data.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "solar_energy": round(solar_energy, 2),
            "wind_energy": round(wind_energy, 2),
            "total_generation": round(total_generation, 2),
            "demand": round(hourly_demand, 2),
            "battery_storage": round(abs(battery_storage), 2),
            "energy_export": round(max(0, surplus), 2),
            "energy_import": round(max(0, -surplus), 2),
            "confidence": 65.0,  # Lower confidence for simulation
            "solar_prediction_interval": {"lower": round(solar_energy * 0.8, 2), "upper": round(solar_energy * 1.2, 2)},
            "wind_prediction_interval": {"lower": round(wind_energy * 0.7, 2), "upper": round(wind_energy * 1.3, 2)}
        })
    
    # Save to CSV
    result = pd.DataFrame(forecast_data)
    forecast_path = os.path.join(data_dir, 'forecast_output.csv')
    result.to_csv(forecast_path, index=False)
    
    print(f"Generated simulation forecast with {len(result)} records")
    
    return result