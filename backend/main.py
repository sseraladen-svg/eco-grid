from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_login import login_required, current_user
import json
import os
import sys
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
FRONTEND_DIR = ROOT_DIR / 'frontend'
DATA_DIR = BASE_DIR / 'data'
DB_FILE = BASE_DIR / 'ecogrid.db'

sys.path.append(str(ROOT_DIR))

from models import db, User, SystemConfiguration
from auth import init_auth, authenticate_user, register_user, logout_user_session, validate_session
from google_auth import init_google_auth
from forecasting.forecast_generation import generate_forecast
from training.train_prophet import train_prophet as train_prophet_model
from forecast import register_forecast_routes
from multigrid import register_multigrid_routes
from export import register_export_routes
from weather import fetch_and_cache_weather

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='')

# Database configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{DB_FILE}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and auth
db.init_app(app)
init_auth(app)
init_google_auth(app)

# Create database tables
with app.app_context():
    db.create_all()


# -----------------------------
# FRONTEND ROUTES
# -----------------------------

@app.route("/")
def login_page():
    return send_from_directory(str(FRONTEND_DIR), "login.html")


@app.route("/setup")
@login_required
def setup_page():
    return send_from_directory(str(FRONTEND_DIR), "setup.html")


@app.route("/forecasting")
@login_required
def forecasting_page():
    """Serve the forecasting page"""
    return send_from_directory(str(FRONTEND_DIR), "forecasting.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Serve the dashboard page"""
    return send_from_directory(str(FRONTEND_DIR), "dashboard.html")


@app.route("/multigrid")
@login_required
def multigrid_page():
    """Serve the Multi-Grid management page"""
    return send_from_directory(str(FRONTEND_DIR), "multigrid.html")


@app.route("/navigation.html")
@login_required
def navigation():
    """Serve the navigation component"""
    return send_from_directory(str(FRONTEND_DIR), "navigation.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(str(FRONTEND_DIR), path)


# -----------------------------
# AUTHENTICATION
# -----------------------------

@app.route("/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Check if this is a registration (name provided) or login
        if name:
            # Register new user
            user, message = register_user(name, email, password, request)
            if user:
                return jsonify({
                    "status": "success", 
                    "message": "Registration successful",
                    "user": user.to_dict(),
                    "redirect": "/setup"
                })
            else:
                return jsonify({"error": message}), 400
        else:
            # Login existing user
            user, message = authenticate_user(email, password, request)
            if user:
                # Check if user has active configuration
                active_config = SystemConfiguration.query.filter_by(
                    user_id=user.id, 
                    is_active=True
                ).first()
                
                redirect_url = "/setup" if not active_config else "/dashboard"
                
                return jsonify({
                    "status": "success", 
                    "message": "Login successful",
                    "user": user.to_dict(),
                    "redirect": redirect_url
                })
            else:
                return jsonify({"error": message}), 401

    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    """User logout endpoint"""
    try:
        logout_user_session()
        return jsonify({"status": "success", "message": "Logout successful"})
    except Exception as e:
        return jsonify({"error": f"Logout failed: {str(e)}"}), 500

@app.route("/api/user/profile")
@login_required
def get_user_profile():
    """Get current user profile"""
    try:
        return jsonify({
            "status": "success",
            "user": current_user.to_dict()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get profile: {str(e)}"}), 500

@app.route("/api/user/configurations")
@login_required
def get_user_configurations():
    """Get user's system configurations"""
    try:
        configurations = SystemConfiguration.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            "status": "success",
            "configurations": [config.to_dict() for config in configurations]
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get configurations: {str(e)}"}), 500


# -----------------------------
# SETUP SAVE
# -----------------------------

@app.route("/submit_setup", methods=["POST"])
@login_required
def submit_setup():
    """Save system configuration for current user"""
    try:
        config = request.json
        
        # Save configuration to database
        system_config = SystemConfiguration(
            user_id=current_user.id,
            name=f"Configuration {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            config_data=json.dumps(config),
            is_active=True
        )
        
        # Deactivate previous configurations
        SystemConfiguration.query.filter_by(user_id=current_user.id).update({'is_active': False})
        
        db.session.add(system_config)
        db.session.commit()
        
        # Generate forecast in background
        try:
            generate_forecast(config)
            return jsonify({
                "status": "success", 
                "message": "Setup saved and forecast generated",
                "config_id": system_config.id
            })
        except Exception as e:
            return jsonify({
                "status": "success", 
                "message": f"Setup saved, forecast generation failed: {str(e)}",
                "config_id": system_config.id
            })
            
    except Exception as e:
        return jsonify({"error": f"Failed to save setup: {str(e)}"}), 500

@app.route("/save_setup", methods=["POST"])
@login_required
def save_setup():
    """Save system configuration without forecast generation"""
    try:
        config = request.json
        
        # Save configuration to database
        system_config = SystemConfiguration(
            user_id=current_user.id,
            name=f"Configuration {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            config_data=json.dumps(config),
            is_active=True
        )
        
        # Deactivate previous configurations
        SystemConfiguration.query.filter_by(user_id=current_user.id).update({'is_active': False})
        
        db.session.add(system_config)
        db.session.commit()
        
        generate_forecast(config)
        
        return jsonify({
            "status": "forecast_generated",
            "config_id": system_config.id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to save setup: {str(e)}"}), 500

@app.route("/api/setup/active")
@login_required
def get_active_setup():
    """Get user's active configuration"""
    try:
        active_config = SystemConfiguration.query.filter_by(
            user_id=current_user.id, 
            is_active=True
        ).first()
        
        if active_config:
            return jsonify({
                "status": "success",
                "configuration": active_config.to_dict()
            })
        else:
            return jsonify({"error": "No active configuration found"}), 404
            
    except Exception as e:
        return jsonify({"error": f"Failed to get configuration: {str(e)}"}), 400


# -----------------------------
# FORECAST API
# -----------------------------

@app.route("/forecast_sample")
@login_required
def get_sample_forecast():
    """Get sample forecast data for demonstration"""
    try:
        print("Generating sample forecast data...")
        
        # Generate 30-day sample forecast data
        forecast_data = []
        base_date = datetime.now()
        
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            
            # Generate realistic sample data with patterns
            solar_val = 4.5 + (i % 10) * 0.8 + (i % 3) * 0.5
            wind_val = 2.8 + (i % 8) * 0.6 + (i % 4) * 0.3
            demand_val = 25 + (i % 12) * 2 + (i % 5) * 1.5
            battery_val = 60 + (i % 18) * 2 + (i % 6) * 1.2
            
            # Ensure realistic values
            solar_val = round(max(0, solar_val), 2)
            wind_val = round(max(0, wind_val), 2)
            demand_val = round(max(10, demand_val), 2)
            battery_val = round(max(0, battery_val), 2)
            
            total_gen = solar_val + wind_val
            net_energy = total_gen - demand_val
            export_val = round(max(0, net_energy * 0.8), 2) if net_energy > 0 else 0
            
            forecast_data.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "solar_energy": solar_val,
                "wind_energy": wind_val,
                "total_generation": round(total_gen, 2),
                "demand": demand_val,
                "battery_storage": battery_val,
                "energy_export": export_val
            })
        
        print(f"Generated {len(forecast_data)} sample forecast records")
        # BUG FIX: same shape mismatch as /forecast - was returning a bare array.
        return jsonify({
            "status": "success",
            "forecast": forecast_data,
            "statistics": _physics_statistics(forecast_data)
        })
        
    except Exception as e:
        print(f"Error generating sample forecast: {str(e)}")
        return jsonify({"error": f"Failed to generate sample data: {str(e)}"}), 500


@app.route("/forecast")
@login_required
def get_forecast():
    """Get forecast data for current user - FIXED VERSION"""
    try:
        # Get user's active configuration from database
        active_config = SystemConfiguration.query.filter_by(
            user_id=current_user.id, 
            is_active=True
        ).first()
        
        if not active_config:
            # Create a default configuration if none exists
            print(f"No active config found for user {current_user.id}, creating default config")
            
            # Save a default configuration
            default_config = {
                "location": {
                    "latitude": "28.6139",
                    "longitude": "77.2090",
                    "altitude": "216",
                    "installation_type": "rooftop",
                    "terrain_type": "urban"
                },
                "solar": {
                    "panel_model": "monocrystalline",
                    "panel_count": "20",
                    "panel_power": "400",
                    "panel_efficiency": "20",
                    "tilt_angle": "30",
                    "azimuth_angle": "180",
                    "installation_type": "fixed",
                    "inverter_efficiency": "95",
                    "system_loss": "10",
                    "shading_factor": "10"
                },
                "wind": {
                    "turbine_model": "small_hawt",
                    "turbine_count": "2",
                    "rated_power": "5000",
                    "cut_in_speed": "3",
                    "cut_out_speed": "25",
                    "hub_height": "30",
                    "rotor_diameter": "10",
                    "turbine_efficiency": "35"
                },
                "battery": {
                    "battery_capacity": "10",
                    "battery_voltage": "48",
                    "charge_efficiency": "95",
                    "discharge_efficiency": "95",
                    "max_discharge_rate": "5"
                },
                "consumption": {
                    "daily_energy_usage": "30",
                    "peak_load": "5",
                    "critical_load": "2",
                    "load_profile_type": "residential"
                }
            }
            
            system_config = SystemConfiguration(
                user_id=current_user.id,
                name=f"Default Configuration {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                config_data=json.dumps(default_config),
                is_active=True
            )
            
            db.session.add(system_config)
            db.session.commit()
            
            print(f"Created default config for user {current_user.id}")
            active_config = system_config
        
        # Check if forecast file exists
        file_path = DATA_DIR / "forecast_output.csv"
        
        if not os.path.exists(file_path):
            # Generate real forecast data based on user parameters
            
            # Parse user configuration
            config = json.loads(active_config.config_data)
            solar_config = config.get('solar', {})
            wind_config = config.get('wind', {})
            battery_config = config.get('battery', {})
            consumption_config = config.get('consumption', {})
            location_config = config.get('location', {})
            
            # Extract parameters
            panel_count = int(solar_config.get('panel_count', 20))
            panel_power = float(solar_config.get('panel_power', 400))
            panel_efficiency = float(solar_config.get('panel_efficiency', 20)) / 100
            turbine_count = int(wind_config.get('turbine_count', 2))
            turbine_rated_power = float(wind_config.get('rated_power', 5000))
            turbine_efficiency = float(wind_config.get('turbine_efficiency', 35)) / 100
            cut_in_speed = float(wind_config.get('cut_in_speed', 3))
            cut_out_speed = float(wind_config.get('cut_out_speed', 25))
            daily_usage = float(consumption_config.get('daily_energy_usage', 30))
            peak_load = float(consumption_config.get('peak_load', 5))
            latitude = float(location_config.get('latitude', 28.6139))
            
            # Generate 30-day forecast
            dates = []
            base_date = datetime.now()
            for i in range(30):
                dates.append((base_date + timedelta(days=i)).strftime('%Y-%m-%d'))
            
            forecast_data = []
            for i, date in enumerate(dates):
                # Calculate solar generation based on panel specs and location
                hour_angle = 15 * (12 - 12)  # Simplified - at noon
                solar_declination = 23.45 * math.sin(math.radians(360 * (284 + i) / 365))
                solar_altitude = math.radians(90 - abs(latitude - solar_declination))
                
                # Solar generation calculation
                solar_irradiance = max(0, 1000 * math.sin(solar_altitude))  # W/m²
                solar_generation = (panel_count * panel_power * panel_efficiency * 
                                  solar_irradiance / 1000 * 0.8) / 1000  # kWh
                solar_generation = max(0, solar_generation)  # Ensure solar generation is never negative
                
                # Wind generation calculation with daily variation
                wind_speed = 8 + 4 * math.sin(i * 0.2) + 2 * random.random()  # m/s with variation
                wind_speed = max(0, wind_speed)  # Ensure wind speed is never negative
                if wind_speed >= cut_in_speed and wind_speed <= cut_out_speed:  # Cut-in and cut-out speeds
                    wind_generation = (turbine_count * turbine_rated_power * turbine_efficiency * 
                                      (wind_speed / 12) ** 3) / 1000  # kWh
                else:
                    wind_generation = 0
                
                # Demand calculation based on usage profile
                hour_factor = 0.6 + 0.4 * math.sin(i * 0.3)  # Daily variation
                demand = daily_usage * hour_factor + peak_load * 0.2 * math.sin(i * 0.5)
                # BUG FIX: the peak_load swing term could exceed the base usage term
                # and push demand negative whenever peak_load was large relative to
                # daily_energy_usage. A site's demand can never actually be negative,
                # so floor it at a small fraction of baseline usage instead of 0 -
                # 0 would look like the site draws no power at all, which isn't real either.
                demand = max(daily_usage * 0.1, demand)
                
                # Battery storage calculation
                total_generation = solar_generation + wind_generation
                net_energy = total_generation - demand
                battery_storage = max(0, net_energy * 0.7) if net_energy > 0 else 0
                
                forecast_data.append({
                    "date": date,
                    "solar_energy": round(solar_generation, 2),
                    "wind_energy": round(wind_generation, 2),
                    "total_generation": round(total_generation, 2),
                    "demand": round(demand, 2),
                    "battery_storage": round(battery_storage, 2),
                    "energy_export": round(max(0, net_energy * 0.8), 2) if net_energy > 0 else 0
                })
            
            print(f"Generated {len(forecast_data)} real forecast records based on user parameters")
            # BUG FIX: this used to return a bare array (jsonify(forecast_data)).
            # The documented API contract - and every frontend page - expects
            # {"status": "success", "forecast": [...], "statistics": {...}}.
            # Returning a bare array meant data.forecast was always undefined
            # on the frontend, so charts/tables silently rendered nothing even
            # though the backend had generated a full 30 days of data.
            return jsonify({
                "status": "success",
                "forecast": forecast_data,
                "statistics": _physics_statistics(forecast_data)
            })
        
        # Read actual forecast data if file exists
        import pandas as pd
        data = pd.read_csv(file_path)
        result = data.tail(30).to_dict(orient="records")
        
        print(f"Loaded {len(result)} actual forecast records")
        return jsonify({
            "status": "success",
            "forecast": result,
            "statistics": _physics_statistics(result)
        })
        
    except Exception as e:
        print(f"Error in forecast endpoint: {str(e)}")
        return jsonify({"error": f"Failed to load forecast: {str(e)}"}), 500


def _physics_statistics(forecast_data):
    """Same statistics shape as the Prophet blueprint (backend/forecast.py),
    computed over the physics-simulated forecast instead of a trained model."""
    if not forecast_data:
        return {'total_solar': 0, 'total_wind': 0, 'average_daily': 0, 'peak_day': 0,
                'trend_direction': '\u2192', 'volatility': 0.0, 'confidence': 0.0,
                'seasonal_pattern': 'Insufficient data'}

    total_values = [d['total_generation'] for d in forecast_data]
    solar_values = [d['solar_energy'] for d in forecast_data]
    wind_values = [d['wind_energy'] for d in forecast_data]

    average_daily = sum(total_values) / len(total_values)
    peak_day = max(total_values)

    if len(total_values) >= 7:
        first_week = sum(total_values[:7]) / 7
        last_week = sum(total_values[-7:]) / 7
        trend = '\u2191' if last_week > first_week * 1.05 else ('\u2193' if last_week < first_week * 0.95 else '\u2192')
    else:
        trend = '\u2192'

    mean_val = average_daily
    variance = sum((x - mean_val) ** 2 for x in total_values) / len(total_values) if total_values else 0
    volatility = (variance ** 0.5 / mean_val * 100) if mean_val > 0 else 0.0

    return {
        'total_solar': round(sum(solar_values), 2),
        'total_wind': round(sum(wind_values), 2),
        'average_daily': round(average_daily, 2),
        'peak_day': round(peak_day, 2),
        'trend_direction': trend,
        'volatility': round(volatility, 1),
        'confidence': 70.0,  # physics simulation, not backtested - fixed moderate confidence
        'seasonal_pattern': 'Simulated',
    }


# -----------------------------
# PROPHET AI ENDPOINTS
# -----------------------------

@app.route("/train_prophet", methods=["POST"])
@login_required
def train_prophet():
    """Train Prophet AI model on real NASA POWER weather data for the
    active configuration's location. This used to fail every time
    (missing data/weather_data.csv) or silently use random fallback data;
    now it fetches real weather and reports honest errors if it can't."""
    active_config = SystemConfiguration.query.filter_by(
        user_id=current_user.id, is_active=True
    ).first()

    if not active_config:
        return jsonify({"error": "No active configuration found. Please complete setup first."}), 400

    try:
        config = json.loads(active_config.config_data)
        location = config.get('location', {})
        latitude = float(location.get('latitude', 28.6139))
        longitude = float(location.get('longitude', 77.2090))
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Invalid location in configuration: {e}"}), 400

    config_dir = DATA_DIR / 'configs' / str(active_config.id)
    weather_path = config_dir / "weather_data.csv"

    try:
        row_count = fetch_and_cache_weather(latitude, longitude, weather_path)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch NASA weather data: {e}"}), 502

    if row_count < 30:
        return jsonify({"error": f"Only {row_count} days of weather data available - not enough to train on."}), 502

    try:
        result = train_prophet_model(weather_path, config_dir)
    except Exception as e:
        return jsonify({"error": f"Failed to train model: {str(e)}"}), 500

    meta = {
        "trained": True,
        "accuracy": result["accuracy"],
        "data_points": result["data_points"],
        "trained_at": datetime.now().isoformat(),
    }
    (config_dir / "model_meta.json").write_text(json.dumps(meta))

    return jsonify({
        "status": "success",
        "message": "Prophet model trained on real NASA POWER weather history",
        "model": meta,
    })


@app.route("/nasa_data", methods=["GET"])
@login_required
def get_nasa_data():
    """Return recent NASA POWER solar/wind data for the active configuration's
    location. Previously this always returned [] because nothing fetched
    the data; now it fetches (and caches) from the real API."""
    active_config = SystemConfiguration.query.filter_by(
        user_id=current_user.id, is_active=True
    ).first()
    if not active_config:
        return jsonify([])

    try:
        config = json.loads(active_config.config_data)
        location = config.get('location', {})
        latitude = float(location.get('latitude', 28.6139))
        longitude = float(location.get('longitude', 77.2090))
    except (ValueError, TypeError, json.JSONDecodeError):
        return jsonify([])

    config_dir = DATA_DIR / 'configs' / str(active_config.id)
    weather_path = config_dir / "weather_data.csv"

    try:
        import pandas as pd
        if not weather_path.exists():
            fetch_and_cache_weather(latitude, longitude, weather_path)
        data = pd.read_csv(weather_path)
        return jsonify(data.tail(100).to_dict(orient="records"))
    except Exception as e:
        print(f"Error loading NASA data: {str(e)}")
        return jsonify([])


# -----------------------------
# REGISTER BLUEPRINTS
# -----------------------------

register_forecast_routes(app)
register_multigrid_routes(app)
register_export_routes(app)


# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == "__main__":
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    app.run(debug=debug_mode, host=host, port=port)