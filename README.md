# EcoGrid AI - Enterprise Energy Management System

<div align="center">
  <img src="https://img.shields.io/badge/Version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/License-Enterprise-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.0%2B-red.svg" alt="Flask">
</div>

## Overview

**EcoGrid AI** is a cutting-edge, enterprise-grade renewable energy management and forecasting system designed for modern energy infrastructure. Powered by advanced AI algorithms and real-time analytics, it provides comprehensive monitoring, prediction, and optimization capabilities for solar, wind, and battery storage systems.

### Key Features

- **AI-Powered Forecasting**: Facebook Prophet integration for accurate 30-day energy predictions
- **Real-time Monitoring**: Live dashboard with instant updates and alerts
- **Multi-Grid Management**: Coordinate and optimize multiple energy grids simultaneously
- **Enterprise Security**: 256-bit encryption, SSO integration, and 2FA support
- **Advanced Analytics**: Comprehensive insights with interactive charts and reports
- **Professional UI**: Modern glass morphism design with responsive layout
- **Export Capabilities**: Data export in JSON, CSV, and Excel formats
- **Health Monitoring**: SmartHeal system for predictive maintenance and diagnostics

## Architecture

### Backend Stack
- **Framework**: Flask 2.0+ with SQLAlchemy ORM
- **Database**: SQLite with session management
- **AI/ML**: Prophet for time-series forecasting
- **Authentication**: Flask-Login with Google OAuth 2.0
- **Security**: bcrypt, Werkzeug, enterprise-grade encryption

### Frontend Stack
- **UI Framework**: TailwindCSS with custom components
- **Charts**: Chart.js for interactive visualizations
- **Maps**: OpenStreetMap integration
- **Icons**: Font Awesome 6.4.0
- **Design**: Glass morphism with animated backgrounds

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 14+ (for development)
- Git

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

3. **Set Environment Variables**
   ```bash
   export GOOGLE_CLIENT_ID="your-google-client-id"
   export GOOGLE_CLIENT_SECRET="your-google-client-secret"
   export SECRET_KEY="your-secret-key"
   ```

4. **Initialize Database**
   ```bash
   python backend/main.py
   ```

5. **Start the Application**
   ```bash
   python backend/main.py
   ```

6. **Access the System**
   - Main Application: http://localhost:5000
   - Dashboard: http://localhost:5000/dashboard
   - API Documentation: http://localhost:5000/api/docs

## Configuration

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4GB | 8GB+ |
| Storage | 10GB | 50GB+ |
| CPU | 2 cores | 4+ cores |
| Network | 1 Mbps | 10+ Mbps |

### Environment Variables

```bash
# Database Configuration
DATABASE_URL="sqlite:///ecogrid.db"

# Security
SECRET_KEY="your-secure-secret-key"
JWT_SECRET_KEY="your-jwt-secret"

# Google OAuth
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# Email Configuration (Optional)
MAIL_SERVER="smtp.gmail.com"
MAIL_PORT=587
MAIL_USERNAME="your-email@gmail.com"
MAIL_PASSWORD="your-app-password"

# System Settings
DEBUG=False
ENVIRONMENT="production"
LOG_LEVEL="INFO"
```

## Features in Detail

### 1. Energy Dashboard
- **Real-time KPIs**: Total generation, demand, battery storage, efficiency
- **Interactive Charts**: Solar, wind, demand, and battery visualizations
- **Performance Metrics**: Historical trends and comparative analysis
- **Alert System**: Real-time notifications for system events

### 2. AI Forecasting
- **30-Day Predictions**: Accurate energy generation forecasts
- **Pattern Recognition**: Daily, weekly, and seasonal patterns
- **Confidence Intervals**: Uncertainty quantification
- **Model Training**: Automatic retraining with new data

### 3. Multi-Grid Management
- **Grid Coordination**: Optimize multiple energy grids
- **Load Balancing**: Intelligent energy distribution
- **Performance Analytics**: Cross-grid metrics and insights

### 4. System Health (SmartHeal)
- **Predictive Maintenance**: Component failure prediction
- **Performance Monitoring**: Real-time efficiency tracking
- **Health Reports**: Comprehensive system diagnostics

### 5. AI Assistant
- **Contextual Insights**: AI-powered energy advice
- **Natural Language**: Conversational interface
- **Real Data Integration**: Uses actual system data

## API Documentation

### Authentication
```bash
# Login
POST /login
{
  "email": "user@example.com",
  "password": "password"
}

# Google OAuth
GET /auth/google
```

### Forecast Endpoints
```bash
# Get Forecast Data
GET /forecast

# Get Sample Data
GET /forecast_sample

# Train Prophet Model
POST /train_prophet
```

### Configuration
```bash
# Save System Configuration
POST /submit_setup

# Get Active Configuration
GET /api/setup/active
```

## Security Features

- **Enterprise Authentication**: Google OAuth 2.0 integration
- **Session Management**: Secure session handling with Flask-Login
- **Data Encryption**: 256-bit AES encryption for sensitive data
- **CSRF Protection**: Cross-site request forgery prevention
- **Input Validation**: Comprehensive input sanitization
- **Security Headers**: OWASP recommended security headers

## Monitoring & Logging

### System Logs
```bash
# Application Logs
tail -f logs/app.log

# Error Logs
tail -f logs/error.log

# Access Logs
tail -f logs/access.log
```

### Performance Metrics
- **Response Time**: API endpoint performance monitoring
- **Database Queries**: Query optimization tracking
- **Memory Usage**: Resource utilization monitoring
- **Error Rates**: System health indicators

## Deployment

### Docker Deployment
```bash
# Build Image
docker build -t ecogrid-ai .

# Run Container
docker run -p 5000:5000 ecogrid-ai
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.main:app

# Using Nginx (Reverse Proxy)
# Configure nginx.conf for production setup
```

## Support & Maintenance

### Troubleshooting
- **Database Issues**: Check database connection and permissions
- **Authentication**: Verify Google OAuth configuration
- **Forecast Errors**: Ensure Prophet dependencies are installed
- **Performance**: Monitor system resources and optimize queries

### Regular Maintenance
- **Database Backups**: Daily automated backups
- **Log Rotation**: Weekly log cleanup
- **Security Updates**: Monthly dependency updates
- **Model Retraining**: Quarterly AI model updates

## License

EcoGrid AI is licensed under the Enterprise License Agreement. See [LICENSE.md](LICENSE.md) for details.

## Support

- **Email**: support@ecogrid-ai.com
- **Documentation**: https://docs.ecogrid-ai.com
- **Community**: https://community.ecogrid-ai.com
- **Issues**: https://github.com/your-org/ecogrid-ai/issues

## Contributing

We welcome contributions from the community! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

### Version 2.0.0 (Latest)
- Enhanced enterprise security features
- Improved AI forecasting accuracy
- New multi-grid management system
- Professional UI redesign
- Advanced analytics dashboard

### Version 1.5.0
- Added SmartHeal health monitoring
- Enhanced export capabilities
- Improved mobile responsiveness
- Bug fixes and performance improvements

---

<div align="center">
  <p>© 2026 EcoGrid AI. Enterprise Energy Management System.</p>
  <p>Built with cutting-edge AI technology for a sustainable future.</p>
</div>
