"""
Export endpoint - the "Export Capabilities" the README claimed but never
had a backend for. Exports the active configuration's forecast as
CSV, JSON, or Excel.
"""

import io
import json

import pandas as pd
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user

from models import SystemConfiguration
from multigrid import _physics_forecast_for_config

export_bp = Blueprint('export', __name__, url_prefix='/api/export')


@export_bp.route('', methods=['GET'])
@login_required
def export_forecast():
    fmt = request.args.get('format', 'json').lower()
    if fmt not in ('json', 'csv', 'xlsx'):
        return jsonify({"error": "format must be one of: json, csv, xlsx"}), 400

    active_config = SystemConfiguration.query.filter_by(
        user_id=current_user.id, is_active=True
    ).first()
    if not active_config:
        return jsonify({"error": "No active configuration found"}), 404

    config_data = json.loads(active_config.config_data)
    forecast = _physics_forecast_for_config(config_data)
    df = pd.DataFrame(forecast)

    if fmt == 'json':
        payload = json.dumps({"config_id": active_config.id, "forecast": forecast}, indent=2)
        mem = io.BytesIO(payload.encode('utf-8'))
        return send_file(mem, mimetype='application/json', as_attachment=True,
                          download_name=f'ecogrid_forecast_{active_config.id}.json')

    if fmt == 'csv':
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        mem = io.BytesIO(buf.getvalue().encode('utf-8'))
        return send_file(mem, mimetype='text/csv', as_attachment=True,
                          download_name=f'ecogrid_forecast_{active_config.id}.csv')

    # xlsx
    mem = io.BytesIO()
    with pd.ExcelWriter(mem, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Forecast')
    mem.seek(0)
    return send_file(mem, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      as_attachment=True, download_name=f'ecogrid_forecast_{active_config.id}.xlsx')


def register_export_routes(app):
    app.register_blueprint(export_bp)
