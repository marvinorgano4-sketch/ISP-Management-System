"""Initialize database for production deployment"""
from app import create_app
from extensions import db
from models import User
import os

def init_database():
    """Initialize database and create default admin user"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            # Create default admin user
            admin = User(
                username='admin',
                full_name='Administrator',
                role='admin'
            )
            admin.set_password('admin123')  # Default password - should be changed!
            
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created (username: admin, password: admin123)")
            print("⚠ IMPORTANT: Change the default password after first login!")
        else:
            print("✓ Admin user already exists")

if __name__ == '__main__':
    init_database()
