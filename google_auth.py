from flask import Blueprint, request, jsonify, redirect, url_for, session
from flask_login import login_user
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from models import User, UserSession, db
from auth import authenticate_user, create_user_session
import os
import json
import secrets

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id.apps.googleusercontent.com')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Create Flask blueprint
google_auth_bp = Blueprint('google_auth', __name__)

# OAuth flow configuration
flow = Flow.from_client_config(
    {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uri": "http://127.0.0.1:5000/auth/google/callback"
        }
    },
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
)

@google_auth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login"""
    # Demo mode - if no Google credentials are set
    if GOOGLE_CLIENT_ID == 'your-google-client-id.apps.googleusercontent.com':
        # Create a demo Google user
        demo_user = {
            'id': 'demo_google_user',
            'name': 'Demo Google User',
            'email': 'demo@gmail.com',
            'picture': 'https://picsum.photos/seed/demo/100/100.jpg'
        }
        
        # Find or create demo user
        user = User.query.filter_by(email=demo_user['email']).first()
        
        if not user:
            user = User(
                name=demo_user['name'],
                email=demo_user['email']
            )
            import random
            import string
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            user.set_password(temp_password)
            
            db.session.add(user)
            db.session.commit()
        
        # Create session and login
        create_user_session(user, request)
        
        # Login with Flask-Login
        login_user(user, remember=True)
        
        # Store Google profile info
        session['google_profile'] = demo_user
        
        # Redirect to frontend with location step
        return redirect('/setup?login_success=true&step=location')
    
    # Real Google OAuth flow
    # Generate state parameter for security
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    
    # Redirect to Google OAuth
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=state,
        prompt='consent'  # Force consent to get refresh token
    )
    
    return redirect(authorization_url)

@google_auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Verify state parameter
        state = request.args.get('state')
        if state != session.get('oauth_state'):
            return jsonify({"error": "Invalid state parameter"}), 400
        
        # Exchange authorization code for tokens
        flow.fetch_token(authorization_response=request.url)
        
        # Get user info from Google
        credentials = flow.credentials
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get()
        
        if not user_info:
            return jsonify({"error": "Failed to get user info from Google"}), 400
        
        # Extract user information
        email = user_info.get('email')
        name = user_info.get('name')
        google_id = user_info.get('id')
        picture = user_info.get('picture')
        
        if not email:
            return jsonify({"error": "Email is required from Google"}), 400
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user
            user = User(
                name=name or email.split('@')[0],
                email=email
            )
            # Generate a random password for Google users
            import random
            import string
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            user.set_password(temp_password)
            
            db.session.add(user)
            db.session.commit()
        
        # Create session and login
        create_user_session(user, request)
        
        # Login with Flask-Login
        login_user(user, remember=True)
        
        # Store Google profile info
        session['google_profile'] = {
            'id': google_id,
            'name': name,
            'email': email,
            'picture': picture
        }
        
        # Redirect to frontend with location step
        return redirect('/setup?login_success=true&step=location')
        
    except Exception as e:
        print(f"Google OAuth error: {str(e)}")
        return redirect('/?error=google_auth_failed')

@google_auth_bp.route('/google/user-info')
def get_google_user_info():
    """Get current Google user info"""
    google_profile = session.get('google_profile')
    if google_profile:
        return jsonify({
            "status": "success",
            "profile": google_profile
        })
    else:
        return jsonify({"error": "No Google profile found"}), 404

def init_google_auth(app):
    """Initialize Google OAuth with Flask app"""
    app.register_blueprint(google_auth_bp, url_prefix='/auth')
