#!/bin/bash

echo "========================================"
echo "ISP Billing System - L SECURITY"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Check if database exists
if [ ! -f "instance/isp_billing.db" ]; then
    echo "Setting up database..."
    flask db upgrade
    echo ""
    
    echo "Creating admin user..."
    python seed_admin.py
    echo ""
fi

echo "========================================"
echo "Starting ISP Billing System..."
echo "========================================"
echo ""
echo "Access the system at:"
echo "  - Local: http://localhost:5000"
echo "  - Network: http://YOUR_IP:5000"
echo ""
echo "Login credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Mikrotik configured at: 192.168.10.5"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Run the application
python app.py
