# ISP Billing System - ANDODNAK ISP

**Network and Data Solution**

Isang web-based na aplikasyon para sa pamamahala ng Internet Service Provider operations na may integration sa Mikrotik RouterOS.

## 🚀 Quick Start (Mabilis na Simula)

### Pinakamadaling Paraan:

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

Tapos na! Buksan ang browser at pumunta sa: **http://localhost:5000**

**Login:**
- Username: `admin`
- Password: `admin123`

**Mikrotik Settings:**
- IP: `192.168.10.5`
- User: `admin`
- Pass: `adminTaboo`

---

### Manual Setup:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup database:**
   ```bash
   flask db upgrade
   python seed_admin.py
   ```

3. **Run:**
   ```bash
   python app.py
   ```

Para sa mas detalyadong instructions, tingnan ang `QUICK_START.md`

---

## Features

- User Authentication at Session Management
- Cliente Management (CRUD operations)
- Real-time Mikrotik PPPoE Connection Monitoring
- Billing Management (Monthly bill generation)
- Payment Processing
- Receipt Generation at Printing
- Dashboard with Statistics at Overview

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with CSRF protection
- **Migrations**: Flask-Migrate
- **Mikrotik Integration**: routeros-api
- **Testing**: pytest, hypothesis (property-based testing)
- **Frontend**: Jinja2 templates with Tailwind CSS

## Project Structure

```
ISP_Management_System/
├── models/          # Database models
├── services/        # Business logic layer
├── routes/          # Flask route blueprints
├── templates/       # Jinja2 templates
├── static/          # Static files (CSS, JS, images)
├── tests/           # Unit and property-based tests
├── app.py           # Application factory
├── config.py        # Configuration settings
├── extensions.py    # Flask extensions initialization
└── requirements.txt # Python dependencies
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` at i-update ang values:

```bash
cp .env.example .env
```

Edit `.env`:
```
SECRET_KEY=your-secret-key-here
MIKROTIK_HOST=10.114.215.133
MIKROTIK_USER=admin
MIKROTIK_PASSWORD=adminTaboo
```

### 3. Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Run the Application

```bash
python app.py
```

Access the application at: http://localhost:5000

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Mikrotik Configuration

Ang sistema ay naka-configure na para sa:
- **Host:** 192.168.10.5
- **Username:** admin
- **Password:** adminTaboo

Siguraduhing:
1. Naka-enable ang Mikrotik API
2. Accessible ang router mula sa computer mo
3. Tama ang IP address, username, at password

Para baguhin ang settings, i-edit ang `config.py` o gumawa ng `.env` file.

## Development

Ang project ay gumagamit ng application factory pattern para sa better testing at modularity. Lahat ng Flask extensions ay initialized sa `extensions.py` at registered sa `create_app()` function.

## License

Proprietary - ANDODNAK ISP
Developer: Marvin Organo
