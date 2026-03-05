import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///isp_billing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mikrotik Configuration
    MIKROTIK_HOST = os.environ.get('MIKROTIK_HOST') or '192.168.10.5'
    MIKROTIK_USER = os.environ.get('MIKROTIK_USER') or 'admin'
    MIKROTIK_PASSWORD = os.environ.get('MIKROTIK_PASSWORD') or 'adminTaboo'
    
    # Session Configuration - Security Features
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # 30-minute session timeout
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'  # Enable in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # WTF Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens
    
    # ZeroTier Configuration
    ZEROTIER_NETWORK_ID = os.environ.get('ZEROTIER_NETWORK_ID')
    ZEROTIER_INTERFACE = os.environ.get('ZEROTIER_INTERFACE', 'zt0')
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    
    # Server Configuration
    BIND_HOST = os.environ.get('BIND_HOST', '0.0.0.0')
    BIND_PORT = int(os.environ.get('BIND_PORT', 5000))
    
    # Bandwidth Monitoring Configuration
    BANDWIDTH_THRESHOLD_RX = float(os.environ.get('BANDWIDTH_THRESHOLD_RX', '200.0'))  # Mbps
    BANDWIDTH_THRESHOLD_TX = float(os.environ.get('BANDWIDTH_THRESHOLD_TX', '100.0'))  # Mbps
    BANDWIDTH_CACHE_TTL = int(os.environ.get('BANDWIDTH_CACHE_TTL', '5'))  # seconds
    BANDWIDTH_UPDATE_INTERVAL = int(os.environ.get('BANDWIDTH_UPDATE_INTERVAL', '10'))  # seconds
    
    @classmethod
    def validate(cls):
        """Validate required configuration values"""
        errors = []
        
        # Validate Flask secret key
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            errors.append(
                "FLASK_SECRET_KEY is not set or using default value.\n"
                "  Fix: Set FLASK_SECRET_KEY in .env file to a strong random string (minimum 32 characters).\n"
                "  Example: FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')"
            )
        
        # Validate ZeroTier configuration (optional but recommended)
        if not cls.ZEROTIER_NETWORK_ID:
            errors.append(
                "ZEROTIER_NETWORK_ID is not set (optional but recommended for remote access).\n"
                "  Fix: Set ZEROTIER_NETWORK_ID in .env file to your ZeroTier network ID.\n"
                "  Example: ZEROTIER_NETWORK_ID=a0cbf4b62a1234567\n"
                "  See ZEROTIER_SETUP.md for setup instructions."
            )
        
        # Validate Firebase configuration (optional but recommended)
        if not cls.FIREBASE_CREDENTIALS_PATH:
            errors.append(
                "FIREBASE_CREDENTIALS_PATH is not set (optional but recommended for cloud database).\n"
                "  Fix: Set FIREBASE_CREDENTIALS_PATH in .env file to the path of your Firebase credentials JSON file.\n"
                "  Example: FIREBASE_CREDENTIALS_PATH=firebase-credentials.json\n"
                "  See FIREBASE_SETUP.md for setup instructions."
            )
        elif not Path(cls.FIREBASE_CREDENTIALS_PATH).exists():
            errors.append(
                f"Firebase credentials file not found: {cls.FIREBASE_CREDENTIALS_PATH}\n"
                f"  Fix: Download your Firebase service account credentials JSON file and save it to {cls.FIREBASE_CREDENTIALS_PATH}\n"
                "  See FIREBASE_SETUP.md for instructions on generating credentials."
            )
        
        if not cls.FIREBASE_PROJECT_ID:
            errors.append(
                "FIREBASE_PROJECT_ID is not set (optional but recommended for cloud database).\n"
                "  Fix: Set FIREBASE_PROJECT_ID in .env file to your Firebase project ID.\n"
                "  Example: FIREBASE_PROJECT_ID=isp-billing-system-12345\n"
                "  See FIREBASE_SETUP.md for setup instructions."
            )
        
        if errors:
            error_message = "Configuration validation errors:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_message)
        
        return True
    
    @classmethod
    def validate_required_only(cls):
        """Validate only critical required configuration (for basic operation)"""
        errors = []
        
        # Only validate Flask secret key for basic operation
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            errors.append(
                "FLASK_SECRET_KEY is not set or using default value.\n"
                "  Fix: Set FLASK_SECRET_KEY in .env file to a strong random string.\n"
                "  Example: FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')"
            )
        
        if errors:
            error_message = "Critical configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_message)
        
        return True
