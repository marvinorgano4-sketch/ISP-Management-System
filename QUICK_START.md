# Quick Start Guide - ISP Billing System

## Paano Papatakbuhin ang System

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Initialize database
flask db upgrade

# Create admin user
python seed_admin.py
```

### 3. Run the Application

```bash
python app.py
```

O kaya:

```bash
flask run --host=0.0.0.0 --port=5000
```

### 4. Access the System

Buksan ang browser at pumunta sa:
- **Local:** http://localhost:5000
- **Network:** http://192.168.10.X:5000 (replace X with your computer's IP)

### 5. Login Credentials

```
Username: admin
Password: admin123
```

## Mikrotik Configuration

Ang system ay naka-configure na para sa:
- **IP Address:** 192.168.10.5
- **Username:** admin
- **Password:** adminTaboo

Kung gusto mong baguhin, i-edit ang `config.py` o gumawa ng `.env` file.

## Creating .env File (Optional)

Gumawa ng `.env` file sa root directory:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///isp_billing.db

# Mikrotik Configuration
MIKROTIK_HOST=192.168.10.5
MIKROTIK_USER=admin
MIKROTIK_PASSWORD=adminTaboo

# Server Configuration
BIND_HOST=0.0.0.0
BIND_PORT=5000
```

## Common Issues

### Error: "No module named 'flask'"
**Solution:** Run `pip install -r requirements.txt`

### Error: "Database not found"
**Solution:** Run `flask db upgrade` to create the database

### Error: "Cannot connect to Mikrotik"
**Solution:** 
1. Check if Mikrotik IP (192.168.10.5) is correct
2. Verify username and password
3. Make sure Mikrotik API is enabled
4. Check if your computer can ping the Mikrotik

### Cannot access from other devices
**Solution:** 
1. Make sure you're running with `--host=0.0.0.0`
2. Check your firewall settings
3. Use your computer's IP address (not localhost)

## Features Available

1. **Dashboard** - Overview ng lahat ng clients, billings, payments
2. **Client Management** - Add, edit, view clients
3. **Billing** - Generate monthly bills
4. **Payments** - Record payments
5. **Receipts** - Generate and print receipts
6. **Mikrotik Integration** - Automatic PPPoE user creation

## Next Steps

Para sa remote access gamit ang ZeroTier at Firebase cloud database:
1. Basahin ang `ZEROTIER_SETUP.md` para sa ZeroTier setup
2. Basahin ang `FIREBASE_SETUP.md` para sa Firebase setup
3. Run ang migration tool para i-migrate ang data sa cloud

## Support

Kung may problema, check ang:
- `DATABASE_SETUP.md` - Database setup details
- `SETUP_GUIDE.md` - Complete setup guide
- `README.md` - System overview

---

**Note:** Ang system ay gumagamit ng SQLite database by default. Para sa production use with remote access, i-setup ang Firebase at ZeroTier (see documentation files).
