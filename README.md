# 🌱 EcoGrid AI
### ⚡ Renewable Energy Forecasting & Management Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-red?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![AI](https://img.shields.io/badge/AI-Prophet-purple?style=for-the-badge&logo=tensorflow&logoColor=white)](https://facebook.github.io/prophet/)
[![NASA](https://img.shields.io/badge/NASA-POWER-blue?style=for-the-badge&logo=nasa&logoColor=white)](https://power.larc.nasa.gov/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

## 🎯 **Project Overview**

**EcoGrid AI** is a comprehensive renewable energy management platform that combines physics-based simulations with AI-powered forecasting to help users optimize their solar and wind energy systems. The platform provides real-time energy predictions, multi-site management, and intelligent analytics for residential and commercial energy installations.

### **Core Capabilities**

- **🧠 AI-Powered Forecasting**: Facebook Prophet integration for accurate 30-day energy predictions
- **🌍 Real-Time Weather Data**: NASA POWER API integration for location-specific weather patterns
- **📊 Physics-Based Simulation**: Solar declination calculations, wind speed modeling, and battery optimization
- **🎯 Multi-Grid Management**: Monitor and compare multiple energy sites simultaneously
- **🔐 Enterprise Security**: Session-based authentication with secure password management
- **🎨 Modern UI**: Dark theme design with interactive charts and responsive layout

---

## ✨ **Key Features**

### **1. Intelligent Energy Forecasting**
- **Physics-Based Simulation**: Solar generation calculated using panel specifications, location, and solar declination
- **Wind Speed Modeling**: Realistic wind patterns with cut-in/cut-out speed thresholds
- **Battery Optimization**: Dynamic charging/discharging based on net energy calculations
- **Demand Modeling**: Realistic usage patterns with seasonal variations
- **Data Validation**: Ensures all generation values are positive and realistic

### **2. AI Model Training**
- **Prophet Integration**: Facebook Prophet for time-series forecasting
- **Automatic Training**: Trains on historical data when available
- **Model Status Tracking**: Real-time training progress and accuracy metrics
- **Fallback Mechanisms**: Graceful degradation to physics simulation when AI models unavailable

### **3. Multi-Site Management**
- **Configuration Management**: Create and manage multiple energy system configurations
- **Site Comparison**: Side-by-side performance analysis across sites
- **Active Site Switching**: One-click configuration changes
- **Performance Metrics**: Key indicators per site (solar, wind, battery, consumption)

### **4. Modern User Interface**
- **Dark Theme Design**: Professional copper/teal color scheme
- **Interactive Charts**: Chart.js integration for data visualization
- **Responsive Layout**: Works seamlessly on desktop and mobile devices
- **Real-Time Updates**: Live data fetching and display
- **Modern Typography**: Space Grotesk, Inter, and IBM Plex Mono fonts

### **5. Data Export System**
- **Multiple Formats**: JSON, CSV, and Excel export options
- **Flexible Export**: Export specific configurations or all data
- **Modern Interface**: Clean modal-based export experience
- **Instant Download**: Direct file delivery with proper formatting

---

## 🛠️ **Technology Stack**

### **Backend**
```yaml
Framework: Flask 2.0+ (Blueprint Architecture)
Database: SQLite with SQLAlchemy ORM
AI/ML: Facebook Prophet for Time-Series Forecasting
Weather: NASA POWER API Integration
Authentication: Flask-Login with Session Management
Data Processing: Pandas & NumPy
Export: openpyxl for Excel, CSV, JSON
Security: bcrypt password hashing
```

### **Frontend**
```yaml
Visualization: Chart.js (Interactive Charts)
Icons: Custom SVG icons
Maps: OpenStreetMap (Leaflet.js) - Optional
Design: Custom CSS with CSS Variables
Typography: Space Grotesk, Inter, IBM Plex Mono
Architecture: Multi-page Application
```

### **DevOps**
```yaml
Containerization: Docker & Docker Compose
Version Control: Git
Environment: python-dotenv
```

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning)

### **Local Development**

```bash
# 1. Clone the repository
git clone https://github.com/sseraladen-svg/eco-grid.git
cd eco-grid

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Start the application
python backend/main.py

# 6. Access the platform
# Open http://localhost:5000 in your browser
```

### **Docker Deployment**

```bash
# 1. Clone the repository
git clone https://github.com/sseraladen-svg/eco-grid.git
cd eco-grid

# 2. Build and run with Docker Compose
docker-compose up -d

# 3. Access the platform
# Open http://localhost:5000 in your browser

# 4. View logs
docker-compose logs -f

# 5. Stop the application
docker-compose down
```

---

## 📱 **Application Pages**

### **1. Login Page (`/`)**
- Modern two-column design with animated curve visualization
- Tabbed interface for Sign In / Create Account
- Password strength meter with real-time validation
- Session management with 7-day persistence
- Google OAuth integration (optional)

### **2. Setup Wizard (`/setup`)**
- 5-step configuration: Location → Solar → Wind → Battery → Consumption
- Interactive map integration (Leaflet.js)
- Live summary sidebar with real-time calculations
- Pre-filled smart defaults for quick setup
- Configuration persistence to database

### **3. Dashboard (`/dashboard`)**
- Real-time KPI cards: Today's generation, 30-day total, peak performance
- Interactive charts: Solar vs wind generation visualization
- Site switcher for quick configuration changes
- 7-day forecast table with daily predictions
- Model status indicator (AI vs Physics)

### **4. Forecasting Center (`/forecasting`)**
- AI model training interface with progress visualization
- Model status indicators (Trained/Training/Not trained)
- Performance statistics: Accuracy, trend, volatility
- 30-day forecast chart with solar and wind lines
- Detailed forecast table with confidence levels
- Export functionality (JSON, CSV, Excel)

### **5. Multi-Grid Management (`/multigrid`)**
- Card-based interface for site configurations
- Active site indicator with visual feedback
- Grid comparison with side-by-side analysis
- Site specifications display (solar, wind, battery)
- Configuration management (add, switch, compare)

---

## 🔌 **API Endpoints**

### **Authentication**
```bash
POST /login                    # User login/registration
POST /logout                   # User logout
GET /api/user/profile          # Get current user profile
GET /api/user/configurations   # Get user configurations
```

### **Configuration**
```bash
POST /submit_setup             # Save system configuration
POST /save_setup               # Save without forecast generation
GET /api/setup/active          # Get active configuration
POST /api/setup/set-active     # Set active configuration
GET /api/setup/compare        # Compare configurations
```

### **Forecasting**
```bash
GET /forecast                  # Physics-based simulation
GET /forecast/model/status    # Check AI model status
POST /forecast/model/train    # Train Prophet model
POST /forecast/generate       # Generate AI forecast
```

### **Export**
```bash
GET /api/export?format=json   # JSON export
GET /api/export?format=csv    # CSV export
GET /api/export?format=xlsx   # Excel export
```

---

## 🏗️ **Project Architecture**

```
EcoGrid-AI/
├── backend/                    # Flask Backend
│   ├── main.py                # Main application & routing
│   ├── models.py              # SQLAlchemy database models
│   ├── auth.py                # Authentication system
│   ├── google_auth.py         # Google OAuth integration
│   ├── forecast.py            # Prophet AI forecasting
│   ├── multigrid.py           # Multi-grid management
│   ├── export.py              # Data export functionality
│   ├── weather.py             # NASA POWER weather API
│   └── data/                  # Runtime data directory
│
├── frontend/                   # Frontend Files
│   ├── login.html             # Login/Registration page
│   ├── dashboard.html         # Main dashboard
│   ├── setup.html             # Setup wizard
│   ├── forecasting.html       # Forecasting center
│   ├── multigrid.html         # Multi-grid management
│   ├── navigation.html        # Navigation component
│   ├── script.js              # General JavaScript
│   ├── forecast-script.js     # Forecasting JavaScript
│   └── assets/css/            # Styling
│
├── forecasting/               # Forecast Generation
│   └── forecast_generation.py # Physics-based forecast
│
├── training/                  # AI Training
│   └── train_prophet.py       # Prophet model training
│
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## 🔧 **Configuration**

### **Environment Variables**

Create a `.env` file in the project root:

```bash
# Application Security
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///backend/ecogrid.db

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
```

### **Database Models**

**Note**: Database files are not included in the repository for security reasons. The database is created automatically when you first run the application.

**User Model:**
- `id`: Primary key
- `name`: User name
- `email`: Unique email address
- `password_hash`: Bcrypt hashed password
- `created_at`: Account creation timestamp
- `last_login`: Last login timestamp
- `is_active`: Account status

**SystemConfiguration Model:**
- `id`: Primary key
- `user_id`: Foreign key to User
- `name`: Configuration name
- `config_data`: JSON configuration data
- `is_active`: Active configuration flag
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Database Setup:**
- SQLite database is automatically created at `backend/ecogrid.db` on first run
- Database schema is initialized automatically via SQLAlchemy
- No manual database setup required

---

## 📊 **Data Flow**

```
User Request → Frontend Interface → API Endpoint → Business Logic
    ↓
Database Operations → AI Model Processing → NASA Weather API
    ↓
Data Validation → Response Generation → Frontend Display
```

---

## 🧪 **Testing**

### **API Testing**

```bash
# Test forecast endpoint
curl http://localhost:5000/forecast

# Test model status
curl http://localhost:5000/forecast/model/status

# Test user profile (requires authentication)
curl http://localhost:5000/api/user/profile
```

### **Database Testing**

```bash
# Access SQLite database
sqlite3 backend/ecogrid.db

# View tables
.tables

# View users
SELECT * FROM user;

# View configurations
SELECT * FROM system_configuration;
```

---

## 🚀 **Deployment Options**

### **1. Docker Deployment (Recommended)**

```bash
# Build and run
docker-compose up -d

# Scale for production
docker-compose up -d --scale ecogrid-ai=3

# View logs
docker-compose logs -f ecogrid-ai
```

### **2. Cloud Deployment**

**Heroku:**
```bash
# Install Heroku CLI
# Login and create app
heroku create ecogrid-ai
heroku addons:add heroku-postgresql

# Deploy
git push heroku main
```

**AWS/Azure/GCP:**
- Use Docker containers with cloud deployment services
- Configure environment variables in cloud platform
- Set up load balancer for high availability
- Configure SSL certificates

### **3. Traditional VPS Deployment**

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv nginx

# Set up application
git clone https://github.com/sseraladen-svg/eco-grid.git
cd eco-grid
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure Nginx reverse proxy
# Configure SSL with Let's Encrypt
# Set up systemd service
```

---

## 🔒 **Security Considerations**

### **Production Deployment Checklist**

- ✅ Change `SECRET_KEY` to a strong random value
- ✅ Use PostgreSQL instead of SQLite for production
- ✅ Enable HTTPS/SSL
- ✅ Configure firewall rules
- ✅ Set up regular database backups
- ✅ Implement rate limiting
- ✅ Add CSRF protection
- ✅ Configure logging and monitoring
- ✅ Set up error tracking (Sentry, etc.)
- ✅ Regular security updates

---

## 🐛 **Troubleshooting**

### **Common Issues**

**1. Negative Values in Forecast**
- **Issue**: Corrupted CSV file in `backend/data/`
- **Solution**: Delete `backend/data/forecast_output.csv` and restart server

**2. Database Locked Error**
- **Issue**: SQLite database locked by another process
- **Solution**: Restart Flask application or check for running processes

**3. Import Errors**
- **Issue**: Missing dependencies
- **Solution**: Run `pip install -r requirements.txt`

**4. Port Already in Use**
- **Issue**: Port 5000 already in use
- **Solution**: Change port in `main.py` or stop conflicting service

**5. Google OAuth Not Working**
- **Issue**: Missing or incorrect Google credentials
- **Solution**: Configure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`

---

## 📈 **Performance Optimization**

### **Database Optimization**
- Use connection pooling
- Add database indexes for frequent queries
- Consider PostgreSQL for production

### **API Optimization**
- Implement response caching
- Add pagination for large datasets
- Use async operations for I/O heavy tasks

### **Frontend Optimization**
- Minify CSS and JavaScript
- Implement lazy loading for charts
- Use CDN for external libraries

---

## 🤝 **Contributing**

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 **Acknowledgments**

- **Facebook Prophet**: Time-series forecasting library
- **NASA POWER API**: Weather and solar data
- **Flask**: Web framework
- **Chart.js**: Data visualization library
- **OpenStreetMap**: Mapping services

---

## 📞 **Support**

For issues, questions, or contributions:
- 📧 Email: support@ecogrid-ai.com
- 🐛 Issues: GitHub Issues
- 📖 Documentation: [API Documentation](API_DOCUMENTATION.md)

---

## 🎯 **Roadmap**

### **Phase 1: Core Features** ✅
- [x] User authentication and session management
- [x] System configuration wizard
- [x] Physics-based energy simulation
- [x] AI model training and forecasting
- [x] Multi-grid management
- [x] Data export functionality

### **Phase 2: Advanced Features** 🚧
- [ ] Real-time WebSocket updates
- [ ] Advanced analytics and reporting
- [ ] Mobile application (React Native)
- [ ] Integration with smart home devices
- [ ] Automated alert system

### **Phase 3: Enterprise Features** 🔮
- [ ] Multi-tenant architecture
- [ ] Advanced role-based access control
- [ ] White-label customization
- [ ] API rate limiting and analytics
- [ ] Enterprise support and SLA

---

<div align="center">

**Built with ❤️ for a sustainable future**

[⬆ Back to Top](#-ecogrid-ai)

</div>
