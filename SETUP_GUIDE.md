# ISP Billing System - Setup Guide

## ✅ Implementation Complete!

Ang ISP Billing System ay tapos na at ready to run!

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables
```bash
cp .env.example .env
```

Edit `.env` kung gusto mo baguhin ang credentials:
```
SECRET_KEY=your-secret-key-here
MIKROTIK_HOST=10.114.215.133
MIKROTIK_USER=admin
MIKROTIK_PASSWORD=adminTaboo
```

### 3. Initialize Database
```bash
flask db upgrade
python seed_admin.py
```

### 4. Run the Application
```bash
python app.py
```

Access at: **http://localhost:5000**

## Default Login Credentials

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **IMPORTANT:** Change the password after first login!

## Features Implemented

✅ User Authentication & Session Management
✅ Client Management (Add, Edit, View, Search)
✅ Real-time Mikrotik PPPoE Monitoring
✅ Monthly Billing Generation
✅ Payment Processing
✅ Receipt Generation & Printing (300px thermal printer)
✅ Dashboard with Statistics
✅ Responsive Design (Mobile, Tablet, Desktop)
✅ Security (CSRF Protection, Password Hashing, Session Expiration)

## System Architecture

```
ISP_Management_System/
├── models/              # Database models (User, Client, Billing, Payment, Receipt)
├── services/            # Business logic (Auth, Client, Billing, Payment, Receipt, Mikrotik, Dashboard)
├── routes/              # Flask blueprints (auth, clients, billing, payments, receipts, dashboard)
├── templates/           # Jinja2 templates with Tailwind CSS
├── tests/               # Unit tests
├── migrations/          # Database migrations
├── instance/            # SQLite database (isp_billing.db)
├── app.py               # Application factory
├── config.py            # Configuration
├── extensions.py        # Flask extensions
└── requirements.txt     # Dependencies
```

## Next Steps (ZeroTier + Firebase)

Gusto mo pa ba i-add ang:
1. **ZeroTier** - Para ma-access remotely kahit saan
2. **Firebase** - Para sa cloud database/storage

Sabihin mo lang kung ready ka na para sa next phase!

## Troubleshooting

### Mikrotik Connection Error
- Check if Mikrotik router is accessible at 10.114.215.133
- Verify API is enabled on Mikrotik
- Check username/password in .env file

### Database Error
- Run `flask db upgrade` to apply migrations
- Run `python seed_admin.py` to create admin user

### Port Already in Use
- Change port in app.py: `app.run(port=5001)`

## Support

For issues or questions, check:
- README.md - Full documentation
- DATABASE_SETUP.md - Database schema and setup
- Design document - .kiro/specs/isp-billing-system/design.md
