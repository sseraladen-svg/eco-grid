"""
NASA POWER weather data fetcher.

Replaces the old stub that always returned an empty array. NASA POWER
(https://power.larc.nasa.gov) is free and requires no API key. We pull
daily solar irradiance and wind speed for a given lat/long and cache it
to disk per-configuration so Prophet has something real to train on.
"""

import csv
import requests
from datetime import datetime, timedelta
from pathlib import Path

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# Parameters: ALLSKY_SFC_SW_DWN = solar irradiance (kWh/m^2/day equivalent),
# WS10M = wind speed at 10m (m/s)
PARAMETERS = "ALLSKY_SFC_SW_DWN,WS10M"


def fetch_weather_history(latitude: float, longitude: float, years: int = 2) -> list[dict]:
    """Fetch daily historical solar/wind data for a location from NASA POWER.

    Returns a list of {date, solar_radiation, wind_speed} dicts, oldest first.
    Raises requests.RequestException on network/API failure — callers should
    handle that explicitly rather than silently falling back to fake data.
    """
    end = datetime.utcnow().date() - timedelta(days=3)  # NASA POWER lags a few days
    start = end - timedelta(days=365 * years)

    params = {
        "parameters": PARAMETERS,
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }

    response = requests.get(NASA_POWER_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    props = payload.get("properties", {}).get("parameter", {})
    solar_series = props.get("ALLSKY_SFC_SW_DWN", {})
    wind_series = props.get("WS10M", {})

    if not solar_series or not wind_series:
        raise ValueError("NASA POWER response missing expected parameters")

    rows = []
    for date_str in sorted(solar_series.keys()):
        solar_val = solar_series.get(date_str)
        wind_val = wind_series.get(date_str)
        # NASA POWER uses -999 as a fill value for missing days — skip those
        if solar_val is None or wind_val is None or solar_val <= -900 or wind_val <= -900:
            continue
        rows.append({
            "date": datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d"),
            "solar_radiation": float(solar_val),
            "wind_speed": float(wind_val),
        })
    return rows


def save_weather_csv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "solar_radiation", "wind_speed"])
        writer.writeheader()
        writer.writerows(rows)


def fetch_and_cache_weather(latitude: float, longitude: float, out_path: Path) -> int:
    """Fetch weather history and write it to out_path. Returns row count."""
    rows = fetch_weather_history(latitude, longitude)
    save_weather_csv(rows, out_path)
    return len(rows)
