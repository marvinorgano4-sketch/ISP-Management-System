"""Pytest configuration and fixtures"""
import pytest
from app import create_app
from extensions import db as _db

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    from config import Config
    
    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        WTF_CSRF_ENABLED = False
    
    app = create_app(TestConfig)
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    """Create database for testing"""
    with app.app_context():
        yield _db
        _db.session.remove()
        _db.drop_all()
        _db.create_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app, db):
    """Create a test user"""
    from models.user import User
    
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(username='admin').first()
        if not user:
            user = User(username='admin', full_name='Test Admin')
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
        
        yield user
