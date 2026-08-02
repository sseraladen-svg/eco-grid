from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import session
from models import User, UserSession, db
from datetime import datetime, timedelta
import secrets
import string

# Initialize login manager
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Load user from database"""
    return User.query.get(int(user_id))

def create_user_session(user, request=None):
    """Create a new user session"""
    # Generate secure session token
    session_token = secrets.token_urlsafe(32)
    
    # Get session details
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent', '')
    
    # Create session record
    user_session = UserSession(
        user_id=user.id,
        session_token=session_token,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days expiry
    )
    
    db.session.add(user_session)
    db.session.commit()
    
    # Store session token in Flask session
    session['session_token'] = session_token
    
    return user_session

def validate_session():
    """Validate current session"""
    session_token = session.get('session_token')
    
    if not session_token:
        return False
    
    user_session = UserSession.query.filter_by(
        session_token=session_token,
        is_active=True
    ).first()
    
    if not user_session or user_session.is_expired():
        # Clean up expired session
        if user_session:
            user_session.is_active = False
            db.session.commit()
        session.pop('session_token', None)
        return False
    
    return True

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    expired_sessions = UserSession.query.filter(
        UserSession.expires_at < datetime.utcnow()
    ).all()
    
    for session_obj in expired_sessions:
        session_obj.is_active = False
    
    db.session.commit()
    
    return len(expired_sessions)

def authenticate_user(email, password, request=None):
    """Authenticate user with email and password"""
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.is_active:
        return None, "Invalid email or password"
    
    if not user.check_password(password):
        return None, "Invalid email or password"
    
    # Update last login
    user.update_last_login()
    
    # Create session
    create_user_session(user, request)
    
    # Login with Flask-Login
    login_user(user, remember=True)
    
    return user, "Login successful"

def register_user(name, email, password, request=None):
    """Register a new user"""
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return None, "Email already registered"
    
    # Validate password
    if len(password) < 8:
        return None, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return None, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return None, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return None, "Password must contain at least one number"
    
    # Create new user
    user = User(
        name=name,
        email=email
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    # Auto-login after registration
    authenticate_user(email, password, request)
    
    return user, "Registration successful"

def logout_user_session():
    """Logout user and invalidate session"""
    session_token = session.get('session_token')
    
    if session_token:
        user_session = UserSession.query.filter_by(session_token=session_token).first()
        if user_session:
            user_session.is_active = False
            db.session.commit()
    
    session.pop('session_token', None)
    logout_user()

def get_user_stats():
    """Get user statistics"""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    recent_logins = User.query.filter(
        User.last_login >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'recent_logins': recent_logins
    }

def init_auth(app):
    """Initialize authentication system"""
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Clean up expired sessions periodically
    @app.before_request
    def cleanup_sessions():
        # Only cleanup occasionally to avoid performance impact
        if secrets.randbelow(100) == 0:  # 1% chance
            cleanup_expired_sessions()
