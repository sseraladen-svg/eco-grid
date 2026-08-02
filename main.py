from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_login import login_required, current_user
import json
import os
import sys
import random
import math
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import db, User, SystemConfiguration
from auth import init_auth, authenticate_user, register_user, logout_user_session, validate_session
from google_auth import init_google_auth
from forecasting.forecast_generation import generate_forecast
from training.train_prophet import train_prophet as train_prophet_model
from forecast import register_forecast_routes

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# Database configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecogrid.db'
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
    return send_from_directory("../frontend", "login.html")


@app.route("/setup")
@login_required
def setup_page():
    return send_from_directory("../frontend", "setup.html")


@app.route("/chatbot")
@login_required
def chatbot_page():
    return send_from_directory("../frontend", "chatbot.html")


@app.route("/forecasting")
@login_required
def forecasting_page():
    """Serve the forecasting page"""
    return send_from_directory("../frontend", "forecasting.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Serve the dashboard page"""
    return send_from_directory("../frontend", "dashboard.html")


@app.route("/smartheal.html")
def smartheal_page():
    """Serve the SmartHeal page"""
    return send_from_directory("../frontend", "smartheal.html")


@app.route("/multigrid.html")
def multigrid_page():
    """Serve the MultiGrid page"""
    return send_from_directory("../frontend", "multigrid.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("../frontend", path)


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
                    "user": user.to_dict()
                })
            else:
                return jsonify({"error": message}), 400
        else:
            # Login existing user
            user, message = authenticate_user(email, password, request)
            if user:
                return jsonify({
                    "status": "success", 
                    "message": "Login successful",
                    "user": user.to_dict()
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
        print("🔄 Generating sample forecast data...")
        
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
        
        print(f"✅ Generated {len(forecast_data)} sample forecast records")
        return jsonify(forecast_data)
        
    except Exception as e:
        print(f"❌ Error generating sample forecast: {str(e)}")
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
        file_path = "data/forecast_output.csv"
        
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
            return jsonify(forecast_data)
        
        # Read actual forecast data if file exists
        import pandas as pd
        data = pd.read_csv(file_path)
        result = data.tail(30).to_dict(orient="records")
        
        print(f"Loaded {len(result)} actual forecast records")
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in forecast endpoint: {str(e)}")
        return jsonify({"error": f"Failed to load forecast: {str(e)}"}), 500


# -----------------------------
# PROPHET AI ENDPOINTS
# -----------------------------

@app.route("/train_prophet", methods=["POST"])
@login_required
def train_prophet():
    """Train Prophet AI model for energy forecasting"""
    try:
        print("Starting Prophet model training...")
        
        # Get user's active configuration
        active_config = SystemConfiguration.query.filter_by(
            user_id=current_user.id, 
            is_active=True
        ).first()
        
        if not active_config:
            return jsonify({"error": "No active configuration found. Please complete setup first."}), 400
        
        # Train the Prophet model
        train_prophet_model()
        
        print("Prophet model training completed successfully")
        return jsonify({
            "status": "success", 
            "message": "Prophet model trained successfully"
        })
        
    except Exception as e:
        print(f"Error training Prophet model: {str(e)}")
        return jsonify({"error": f"Failed to train model: {str(e)}"}), 500

@app.route("/forecast_prophet", methods=["GET"])
@login_required
def forecast_prophet():
    """Get Prophet AI forecast data with automatic training"""
    try:
        print("Generating Prophet forecast...")
        
        # Check if trained models exist, if not train automatically
        solar_forecast_path = "../data/solar_forecast.csv"
        wind_forecast_path = "../data/wind_forecast.csv"
        
        if not os.path.exists(solar_forecast_path) or not os.path.exists(wind_forecast_path):
            print("No trained models found. Training Prophet AI automatically...")
            try:
                # Train the model automatically
                train_prophet_model()
                print("✅ Prophet AI trained automatically!")
                
                # Now generate forecast with trained models
                return generate_trained_prophet_forecast()
            except Exception as e:
                print(f"❌ Auto-training failed: {e}")
                print("🔄 Falling back to sample forecast...")
                return generate_sample_prophet_forecast()
        else:
            print("✅ Trained models found. Using trained forecast...")
            return generate_trained_prophet_forecast()
        
    except Exception as e:
        print(f"Error generating Prophet forecast: {str(e)}")
        return generate_sample_prophet_forecast()

def generate_trained_prophet_forecast():
    """Generate forecast using trained Prophet models"""
    try:
        import pandas as pd
        
        # Read trained forecast data
        solar_df = pd.read_csv("../data/solar_forecast.csv")
        wind_df = pd.read_csv("../data/wind_forecast.csv")
        
        print(f"📊 Using trained models: Solar={len(solar_df)} records, Wind={len(wind_df)} records")
        
        # Combine forecasts and calculate statistics
        forecast_data = []
        for i in range(min(len(solar_df), len(wind_df), 30)):  # Max 30 days
            # Ensure non-negative values
            solar_val = max(0, float(solar_df.iloc[i]['yhat']) if 'yhat' in solar_df.columns else 0)
            wind_val = max(0, float(wind_df.iloc[i]['yhat']) if 'yhat' in wind_df.columns else 0)
            
            forecast_data.append({
                "date": solar_df.iloc[i]['ds'] if 'ds' in solar_df.columns else f"2024-01-{i+1:02d}",
                "solar_energy": round(solar_val, 2),
                "wind_energy": round(wind_val, 2),
                "total_generation": round(solar_val + wind_val, 2),
                "demand": round(30 + (i % 10) * 2, 2),
                "battery_storage": round(50 + (i % 20) * 2, 2)
            })
        
        # Calculate Prophet AI statistics
        stats = calculate_prophet_statistics(forecast_data)
        
        # Add model_type to statistics
        stats['model_type'] = 'trained'
        
        result = {
            "forecast": forecast_data,
            "statistics": stats
        }
        
        print(f"✅ Generated trained forecast: {len(result['forecast'])} records")
        print(f"📈 Statistics: {result['statistics']}")
        print(f"🔍 Result structure: {list(result.keys())}")
        print(f"🔍 Statistics structure: {list(stats.keys())}")
        print(f"🔍 About to send JSON response:")
        print(f"🔍 Forecast sample: {result['forecast'][0] if result['forecast'] else 'None'}")
        print(f"🔍 Statistics sample: {result['statistics']}")
        print(f"🔍 Full JSON being sent: {json.dumps(result, indent=2)[:1000]}...")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error using trained models: {e}")
        print("🔄 Falling back to sample forecast...")
        return generate_sample_prophet_forecast()

def generate_sample_prophet_forecast():
    """Generate sample Prophet forecast with proper format"""
    print("Generating sample Prophet forecast...")
    
    from datetime import datetime, timedelta
    import random
    import json
    
    forecast_data = []
    base_date = datetime.now()
    
    for i in range(30):
        current_date = base_date + timedelta(days=i)
        
        # Generate realistic sample data with some variation
        solar_base = 25 + 10 * abs(0.5 - random.random())  # 15-35 kWh
        wind_base = 15 + 8 * abs(0.5 - random.random())   # 7-23 kWh
        
        solar_val = round(solar_base, 2)
        wind_val = round(wind_base, 2)
        
        forecast_data.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "solar_energy": solar_val,
            "wind_energy": wind_val,
            "total_generation": round(solar_val + wind_val, 2),
            "demand": round(30 + (i % 8) * 2, 2),
            "battery_storage": round(50 + (i % 15) * 3, 2)
        })
    
    stats = calculate_prophet_statistics(forecast_data)
    
    result = {
        "forecast": forecast_data,
        "statistics": stats
    }
    
    print(f"Generated Prophet forecast: {len(result['forecast'])} records")
    print(f"Statistics: {result['statistics']}")
    print(f"Result structure: {list(result.keys())}")
    print(f"Forecast sample: {json.dumps(result['forecast'][0], indent=2)}")
    print(f"Full result JSON: {json.dumps(result, indent=2)[:500]}...")
    
    return jsonify(result)

def calculate_prophet_statistics(forecast_data):
    """Calculate Prophet AI statistics from forecast data"""
    if not forecast_data:
        return {
            "accuracy": 0,
            "trend_direction": "→",
            "volatility": 0,
            "peak_prediction": 0
        }
    
    # Extract total generation values
    generation_values = [item["total_generation"] for item in forecast_data]
    
    # Calculate accuracy (based on consistency)
    if len(generation_values) > 1:
        mean_val = sum(generation_values) / len(generation_values)
        variance = sum((x - mean_val) ** 2 for x in generation_values) / len(generation_values)
        accuracy = max(0, min(100, 100 - (variance / mean_val * 100) if mean_val > 0 else 0))
    else:
        accuracy = 85  # Default accuracy
    
    # Calculate trend direction
    if len(generation_values) >= 7:
        first_week = sum(generation_values[:7]) / 7
        last_week = sum(generation_values[-7:]) / 7
        
        if last_week > first_week * 1.05:
            trend = "↑"
        elif last_week < first_week * 0.95:
            trend = "↓"
        else:
            trend = "→"
    else:
        trend = "→"
    
    # Calculate volatility (coefficient of variation)
    if len(generation_values) > 1:
        mean_val = sum(generation_values) / len(generation_values)
        std_dev = (sum((x - mean_val) ** 2 for x in generation_values) / len(generation_values)) ** 0.5
        volatility = (std_dev / mean_val * 100) if mean_val > 0 else 0
        volatility = round(volatility, 1)
    else:
        volatility = 15.0
    
    # Find peak prediction
    peak_prediction = max(generation_values) if generation_values else 0
    
    return {
        "accuracy": round(accuracy, 1),
        "trend_direction": trend,
        "volatility": volatility,
        "peak_prediction": round(peak_prediction, 2)
    }

@app.route("/nasa_data", methods=["GET"])
@login_required
def get_nasa_data():
    """Get NASA solar data for reference"""
    try:
        # Check if NASA data file exists
        nasa_data_path = "data/nasa_solar_data.csv"
        
        if not os.path.exists(nasa_data_path):
            return jsonify([])  # Return empty array if no NASA data
        
        # Read NASA data
        import pandas as pd
        data = pd.read_csv(nasa_data_path)
        result = data.tail(100).to_dict(orient="records")  # Return last 100 records
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error loading NASA data: {str(e)}")
        return jsonify([])  # Return empty array on error


# -----------------------------
# REGISTER BLUEPRINTS
# -----------------------------

# Register forecast API routes
register_forecast_routes(app)


# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)