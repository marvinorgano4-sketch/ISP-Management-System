"""Fix client data - set default plan and amount for clients with missing data"""
from app import create_app
from models.client import Client
from extensions import db

app = create_app()

with app.app_context():
    # Get all clients
    clients = Client.query.all()
    
    print(f"Found {len(clients)} clients")
    
    # Fix clients with missing plan data
    fixed_count = 0
    for client in clients:
        if not client.plan_name or client.plan_name == "Default Plan":
            client.plan_name = "Basic Plan"
            fixed_count += 1
        
        if not client.plan_amount or client.plan_amount == 0.0:
            client.plan_amount = 500.0
            fixed_count += 1
    
    # Commit changes
    db.session.commit()
    
    print(f"Fixed {fixed_count} client records")
    print("\nUpdated clients:")
    for client in clients[:5]:
        print(f"  {client.pppoe_username}: {client.plan_name} - ₱{client.plan_amount}")
