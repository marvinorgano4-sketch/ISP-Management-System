@echo off
echo ========================================
echo ISP Billing System - L SECURITY
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Check if database exists
if not exist "instance\isp_billing.db" (
    echo Setting up database...
    flask db upgrade
    echo.
    
    echo Creating admin user...
    python seed_admin.py
    echo.
)

echo ========================================
echo Starting ISP Billing System...
echo ========================================
echo.
echo Access the system at:
echo   - Local: http://localhost:5000
echo   - Network: http://YOUR_IP:5000
echo.
echo Login credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Mikrotik configured at: 192.168.10.5
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run the application
python app.py
