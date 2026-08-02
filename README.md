# EcoGrid AI - Renewable Energy Management System

<div align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.0%2B-red.svg" alt="Flask">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg" alt="Status">
</div>

## Overview

**EcoGrid AI** is a comprehensive renewable energy management and forecasting system designed for solar, wind, and battery storage optimization. Built with Flask and powered by AI algorithms, it provides accurate energy predictions, multi-grid management, and enterprise-grade monitoring capabilities.

### Key Features

- **AI-Powered Forecasting**: Facebook Prophet integration for 30-day energy predictions
- **Multi-Grid Management**: Monitor and optimize multiple energy sites simultaneously
- **Real-time Dashboard**: Live metrics, charts, and performance analytics
- **Data Export**: Export forecast data in JSON, CSV, and Excel formats
- **NASA Weather Integration**: Real-time weather data from NASA POWER API
- **Setup Wizard**: 5-step configuration wizard for system parameters
- **Modern Authentication**: Email/password with session management
- **Professional UI**: Clean, responsive interface with interactive charts

## Technology Stack

### Backend
- **Framework**: Flask 2.0+ with Blueprint architecture
- **Database**: SQLite with SQLAlchemy ORM
- **AI/ML**: Prophet for time-series forecasting
- **Authentication**: Flask-Login with session management
- **Weather API**: NASA POWER for real-time weather data

### Frontend
- **Charts**: Chart.js for interactive visualizations
- **Icons**: Font Awesome 6.4.0
- **Maps**: OpenStreetMap (Leaflet.js)
- **Design**: Modern, responsive CSS

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/ecogrid-ai.git
   cd ecogrid-ai
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Application**
   ```bash
   python backend/main.py
   ```

4. **Access the System**
   - Main Application: http://localhost:5000
   - Login Page: http://localhost:5000/login.html
   - Dashboard: http://localhost:5000/dashboard.html

## Features in Detail

### 1. Authentication System
- **Email/Password Login**: Secure authentication with session management
- **Registration**: New user account creation with validation
- **Password Strength**: Real-time password strength indicator
- **Modern UI**: Two-column login design with tabbed interface

### 2. Setup Wizard
- **5-Step Configuration**: Location, Solar, Wind, Battery, Consumption
- **Map Integration**: Select location using interactive map
- **Pre-filled Defaults**: Sensible defaults for quick setup
- **Live Summary**: Real-time configuration summary sidebar

### 3. Energy Dashboard
- **Real-time Metrics**: Generation, consumption, battery storage, efficiency
- **Interactive Charts**: Solar vs demand visualization
- **Active Site Indicator**: Shows currently active configuration
- **Export Functionality**: Quick data export from dashboard

### 4. AI Forecasting
- **30-Day Predictions**: Accurate energy generation forecasts
- **Training Progress**: Visual feedback during model training
- **Model Status**: Shows AI model training state
- **Statistics**: Accuracy, trend, volatility, and peak predictions

### 5. Multi-Grid Management
- **Card-Based Interface**: Visual grid cards for each site
- **Active Site Switching**: Easy switching between configurations
- **Grid Comparison**: Compare multiple sites side-by-side
- **Metrics Display**: Key metrics per site

### 6. Data Export
- **Multiple Formats**: JSON, CSV, Excel export options
- **Modern Modal**: Clean export interface
- **Download Functionality**: Direct file download

## API Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API documentation including:
- All endpoints with input/output formats
- Authentication requirements
- Configuration data structures
- Forecast data structures
- Error handling guidelines

### Key Endpoints

```bash
# Authentication
POST /login

# Configuration
POST /submit_setup
GET /api/setup/active
GET /api/setup/compare?configs=1,2,3

# Forecasting
GET /forecast
GET /forecast_prophet
POST /train_prophet

# Export
GET /api/export?format=json
GET /api/export?format=csv
GET /api/export?format=xlsx

# Multi-Grid
GET /api/user/configurations
POST /api/setup/set-active
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Security
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (default: SQLite)
DATABASE_URL=sqlite:///ecogrid.db

# Session Configuration
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=604800
```

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4GB | 8GB+ |
| Storage | 10GB | 50GB+ |
| CPU | 2 cores | 4+ cores |
| Python | 3.8+ | 3.10+ |

## Project Structure

```
EcoGrid-AI/
├── backend/
│   ├── auth.py              # Authentication routes
│   ├── forecast.py          # Forecasting endpoints
│   ├── google_auth.py       # Google OAuth (optional)
│   ├── main.py              # Flask application entry
│   ├── models.py            # Database models
│   ├── export.py            # Data export functionality
│   ├── weather.py           # NASA weather integration
│   └── multigrid.py         # Multi-grid management
├── frontend/
│   ├── assets/
│   │   └── css/
│   │       └── enterprise.css
│   ├── login.html           # Login/Register page
│   ├── dashboard.html       # Main dashboard
│   ├── setup.html           # Setup wizard
│   ├── forecasting.html     # Forecasting page
│   ├── multigrid.html       # Multi-grid management
│   ├── navigation.html      # Navigation component
│   ├── script.js            # Common JavaScript
│   └── forecast-script.js   # Forecasting scripts
├── training/
│   └── train_prophet.py      # Prophet model training
├── requirements.txt         # Python dependencies
├── API_DOCUMENTATION.md     # Complete API docs
└── README.md               # This file
```

## Deployment

### Development Server
```bash
python backend/main.py
```

### Production Server (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.main:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.main:app"]
```

## Dependencies

Key Python packages:
- Flask 2.0+
- Flask-Login
- SQLAlchemy
- Prophet (AI forecasting)
- pandas
- numpy
- openpyxl (Excel export)
- requests (NASA API)

See [requirements.txt](requirements.txt) for complete list.

## Troubleshooting

### Common Issues

**Database Error**: Delete `ecogrid.db` and restart the application
```bash
rm ecogrid.db
python backend/main.py
```

**Import Errors**: Ensure all dependencies are installed
```bash
pip install -r requirements.txt
```

**Port Already in Use**: Change port in `backend/main.py`
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Use different port
```

## Security Notes

- Uses session-based authentication
- CSRF protection recommended for production
- HTTPS recommended for production deployment
- Secret key should be set in environment variables
- Database should be properly secured in production

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

<div align="center">
  <p>© 2026 EcoGrid AI. Renewable Energy Management System.</p>
  <p>Built with Flask, Prophet, and modern web technologies.</p>
</div>
