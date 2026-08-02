"""
Multi-Grid: manage and compare multiple site configurations for one user.

The data model already supported multiple SystemConfiguration rows per
user; this blueprint is what was missing - the ability to list them,
switch which one is active, and compare their forecasts side by side.
"""

import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from models import db, SystemConfiguration

multigrid_bp = Blueprint('multigrid', __name__, url_prefix='/api/setup')


@multigrid_bp.route('/set-active', methods=['POST'])
@login_required
def set_active_config():
    """Mark one of the current user's configs as active; deactivate the rest."""
    data = request.get_json(silent=True) or {}
    config_id = data.get('config_id')
    if not config_id:
        return jsonify({"error": "config_id is required"}), 400

    config = SystemConfiguration.query.filter_by(
        id=config_id, user_id=current_user.id
    ).first()
    if not config:
        return jsonify({"error": "Configuration not found"}), 404

    SystemConfiguration.query.filter_by(user_id=current_user.id).update({'is_active': False})
    config.is_active = True
    db.session.commit()

    return jsonify({"status": "success", "configuration": config.to_dict()})


def _physics_forecast_for_config(config_data: dict) -> list[dict]:
    """Same physics-based 30-day model used by /forecast, factored out so
    Multi-Grid comparisons don't need a trained Prophet model per site."""
    solar_config = config_data.get('solar', {})
    wind_config = config_data.get('wind', {})
    consumption_config = config_data.get('consumption', {})
    location_config = config_data.get('location', {})

    panel_count = int(solar_config.get('panel_count', 20))
    panel_power = float(solar_config.get('panel_power', 400))
    panel_efficiency = float(solar_config.get('panel_efficiency', 20)) / 100
    turbine_count = int(wind_config.get('turbine_count', 2))
    turbine_rated_power = float(wind_config.get('rated_power', 5000))
    turbine_efficiency = float(wind_config.get('turbine_efficiency', 35)) / 100
    cut_in_speed = float(wind_config.get('cut_in_speed', 3))
    cut_out_speed = float(wind_config.get('cut_out_speed', 25))
    daily_usage = float(consumption_config.get('daily_energy_usage', 30))
    latitude = float(location_config.get('latitude', 28.6139))

    base_date = datetime.now()
    forecast_data = []
    for i in range(30):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')

        solar_declination = 23.45 * math.sin(math.radians(360 * (284 + i) / 365))
        solar_altitude = math.radians(90 - abs(latitude - solar_declination))
        solar_irradiance = max(0, 1000 * math.sin(solar_altitude))
        solar_generation = max(0, (panel_count * panel_power * panel_efficiency *
                                    solar_irradiance / 1000 * 0.8) / 1000)

        wind_speed = max(0, 8 + 4 * math.sin(i * 0.2) + 2 * random.random())
        if cut_in_speed <= wind_speed <= cut_out_speed:
            wind_generation = (turbine_count * turbine_rated_power * turbine_efficiency *
                                (wind_speed / 12) ** 3) / 1000
        else:
            wind_generation = 0

        hour_factor = 0.6 + 0.4 * math.sin(i * 0.3)
        demand = daily_usage * hour_factor

        total_generation = solar_generation + wind_generation
        forecast_data.append({
            "date": date,
            "solar_energy": round(solar_generation, 2),
            "wind_energy": round(wind_generation, 2),
            "total_generation": round(total_generation, 2),
            "demand": round(demand, 2),
        })
    return forecast_data


@multigrid_bp.route('/compare')
@login_required
def compare_configs():
    """?configs=1,2,3 -> forecast summary for each, scoped to current user."""
    ids_param = request.args.get('configs', '')
    try:
        ids = [int(x) for x in ids_param.split(',') if x.strip()]
    except ValueError:
        return jsonify({"error": "configs must be a comma-separated list of IDs"}), 400

    if not ids:
        return jsonify({"error": "configs query param is required, e.g. ?configs=1,2"}), 400

    configs = SystemConfiguration.query.filter(
        SystemConfiguration.id.in_(ids),
        SystemConfiguration.user_id == current_user.id
    ).all()

    if not configs:
        return jsonify({"error": "No matching configurations found"}), 404

    results = []
    for config in configs:
        config_data = json.loads(config.config_data)
        forecast = _physics_forecast_for_config(config_data)
        total_gen = sum(d['total_generation'] for d in forecast)
        results.append({
            "config_id": config.id,
            "name": config.name,
            "is_active": config.is_active,
            "location": config_data.get('location', {}),
            "forecast": forecast,
            "total_30day_generation": round(total_gen, 2),
            "average_daily_generation": round(total_gen / len(forecast), 2) if forecast else 0,
        })

    return jsonify({"status": "success", "configurations": results})


def register_multigrid_routes(app):
    app.register_blueprint(multigrid_bp)
