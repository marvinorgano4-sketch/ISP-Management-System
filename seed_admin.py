"""Seed script to create initial admin user"""
from app import create_app
from extensions import db
from models import User

def seed_admin():
    """Create initial admin user if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print("Admin user already exists!")
            return
        
        # Create new admin user
        admin = User(
            username='admin',
            full_name='System Administrator'
        )
        admin.set_password('admin123')  # Default password - should be changed after first login
        
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("\nIMPORTANT: Please change the default password after first login!")

if __name__ == '__main__':
    seed_admin()
