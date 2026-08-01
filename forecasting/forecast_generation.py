import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def to_float(value, default=0.0):
    try:
        if value == "" or value is None:
            return default
        return float(value)
    except:
        return default


def generate_forecast(config):
    """
    Generate 30-day energy forecast based on user configuration
    """
    print("Generating 30-day energy forecast...")
    
    # Get user configuration
    solar = config.get("solar", {})
    wind = config.get("wind", {})
    battery = config.get("battery", {})
    consumption = config.get("consumption", {})
    location = config.get("location", {})

    # Extract solar parameters
    panel_power = to_float(solar.get("panel_power", 400))  # Watts per panel
    panel_count = to_float(solar.get("panel_count", 10))
    panel_efficiency = to_float(solar.get("panel_efficiency", 20)) / 100  # Convert to decimal
    system_loss = to_float(solar.get("system_loss", 15)) / 100  # Convert to decimal
    tilt_angle = to_float(solar.get("tilt_angle", 30))
    azimuth_angle = to_float(solar.get("azimuth_angle", 180))

    # Extract wind parameters
    turbine_power = to_float(wind.get("rated_power", 5000))  # Watts per turbine
    turbine_count = to_float(wind.get("turbine_count", 2))
    turbine_efficiency = to_float(wind.get("turbine_efficiency", 35)) / 100  # Convert to decimal
    cut_in_speed = to_float(wind.get("cut_in_speed", 3))
    cut_out_speed = to_float(wind.get("cut_out_speed", 25))

    # Extract battery parameters
    battery_capacity = to_float(battery.get("battery_capacity", 13.5))  # kWh
    charge_efficiency = to_float(battery.get("charge_efficiency", 95)) / 100
    discharge_efficiency = to_float(battery.get("discharge_efficiency", 95)) / 100

    # Extract consumption parameters
    daily_demand = to_float(consumption.get("daily_energy_usage", 30))  # kWh per day
    peak_load = to_float(consumption.get("peak_load", 5))  # kW
    load_profile_type = consumption.get("load_profile_type", "residential")

    # Generate 30-day forecast data
    dates = []
    forecast_data = []
    
    base_date = datetime.now()
    
    # Load weather data if available, otherwise use simulated data
    try:
        weather_df = pd.read_csv("data/weather_data.csv")
        print("Using real weather data")
    except:
        print("No weather data found, using simulated data")
        weather_df = None
    
    for i in range(30):
        current_date = base_date + timedelta(days=i)
        dates.append(current_date.strftime('%Y-%m-%d'))
        
        # Simulate weather patterns
        day_of_year = current_date.timetuple().tm_yday
        hour_factor = 1.0  # Daily average
        
        # Seasonal variation for solar (stronger in summer)
        solar_seasonal = 0.7 + 0.3 * np.sin(2 * np.pi * day_of_year / 365)
        
        # Daily solar radiation pattern (5.5 peak sun hours average)
        if weather_df is not None and i < len(weather_df):
            solar_radiation = to_float(weather_df.iloc[i].get('solar_radiation', 5.0))
            wind_speed = to_float(weather_df.iloc[i].get('wind_speed', 3.5))
        else:
            # Simulated weather
            solar_radiation = 5.0 * solar_seasonal * (0.8 + 0.2 * np.random.random())
            wind_speed = 3.5 * (0.7 + 0.3 * np.random.random())
        
        # Calculate solar energy generation
        # Solar energy = solar_radiation * panel_power * panel_count * efficiency * system_loss_factor
        solar_energy = (
            solar_radiation *  # kWh/m²/day
            panel_power *  # Watts per panel
            panel_count *  # Number of panels
            panel_efficiency *  # Panel efficiency
            (1 - system_loss) *  # System losses
            5.5 / 1000  # Peak sun hours and convert to kWh
        )
        
        # Calculate wind energy generation
        # Wind energy depends on wind speed and turbine characteristics
        if wind_speed < cut_in_speed or wind_speed > cut_out_speed:
            wind_energy = 0
        else:
            # Simplified wind power calculation
            wind_energy = (
                wind_speed ** 2 *  # Wind speed squared (simplified)
                turbine_power *  # Rated power per turbine
                turbine_count *  # Number of turbines
                turbine_efficiency *  # Turbine efficiency
                0.1 / 1000  # Conversion factor
            )
        
        # Total generation
        total_generation = solar_energy + wind_energy
        
        # Load profile based on time of day
        if load_profile_type == "residential":
            # Residential: higher in morning and evening
            hourly_demand = daily_demand / 24 * (0.8 + 0.4 * np.sin(2 * np.pi * i / 24))
        elif load_profile_type == "commercial":
            # Commercial: higher during business hours
            hourly_demand = daily_demand / 24 * (0.6 + 0.8 * np.sin(2 * np.pi * (i - 6) / 24))
        else:
            # Industrial: relatively constant
            hourly_demand = daily_demand / 24
        
        # Battery storage calculation
        surplus = total_generation - hourly_demand
        
        if surplus > 0:
            # Store excess energy (limited by battery capacity and charge efficiency)
            charge_amount = min(surplus * charge_efficiency, 
                              battery_capacity * 0.2)  # Max 20% charge per hour
            battery_storage = charge_amount
        else:
            # Discharge battery to cover deficit (limited by discharge efficiency)
            discharge_amount = min(abs(surplus) / discharge_efficiency, 
                                 battery_capacity * 0.2)  # Max 20% discharge per hour
            battery_storage = -discharge_amount
        
        # Store forecast data
        forecast_data.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "solar_energy": round(solar_energy, 2),
            "wind_energy": round(wind_energy, 2),
            "total_generation": round(total_generation, 2),
            "demand": round(hourly_demand, 2),
            "battery_storage": round(abs(battery_storage), 2),
            "energy_export": round(max(0, surplus), 2),
            "energy_import": round(max(0, -surplus), 2)
        })
    
    # Create DataFrame and save to CSV
    result = pd.DataFrame(forecast_data)
    
    # Ensure data directory exists
    import os
    os.makedirs("../data", exist_ok=True)
    
    result.to_csv("../data/forecast_output.csv", index=False)
    
    print(f"Generated 30-day forecast with {len(result)} records")
    print(f"Total solar generation: {result['solar_energy'].sum():.2f} kWh")
    print(f"Total wind generation: {result['wind_energy'].sum():.2f} kWh")
    print(f"Total generation: {result['total_generation'].sum():.2f} kWh")
    print(f"Total demand: {result['demand'].sum():.2f} kWh")
    
    return result