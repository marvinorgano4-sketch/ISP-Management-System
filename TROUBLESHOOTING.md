# Troubleshooting Guide - ISP Billing System

## Common Problems at Solutions

### 1. Hindi Makapag-install ng Dependencies

**Error:** `pip: command not found` o `python: command not found`

**Solution:**
- I-install ang Python 3.8 o mas bago
- Windows: Download from python.org
- Linux: `sudo apt install python3 python3-pip`
- Mac: `brew install python3`

---

### 2. Database Errors

**Error:** `OperationalError: no such table`

**Solution:**
```bash
# Delete old database
rm instance/isp_billing.db

# Recreate database
flask db upgrade
python seed_admin.py
```

**Error:** `flask: command not found`

**Solution:**
```bash
# Use python -m flask instead
python -m flask db upgrade
```

---

### 3. Cannot Connect to Mikrotik

**Error:** `Connection refused` o `Timeout`

**Possible Causes at Solutions:**

1. **Mali ang IP Address**
   - Check: Ping the Mikrotik
   ```bash
   ping 192.168.10.5
   ```
   - Kung hindi nag-reply, check ang IP address sa Mikrotik

2. **API Hindi Enabled**
   - Login sa Mikrotik Winbox
   - Go to: IP → Services
   - Enable ang "api" service
   - Default port: 8728

3. **Mali ang Username/Password**
   - Verify sa Mikrotik: System → Users
   - Update sa `config.py` kung iba

4. **Firewall Blocking**
   - Check Mikrotik firewall rules
   - Allow port 8728 from your computer's IP

---

### 4. Cannot Access from Other Devices

**Problem:** Localhost works pero hindi makita sa ibang device

**Solution:**

1. **Check if running with correct host:**
   ```bash
   python app.py
   # Should show: Running on http://0.0.0.0:5000
   ```

2. **Get your computer's IP:**
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` o `ip addr`
   - Look for 192.168.x.x

3. **Access using your IP:**
   ```
   http://192.168.10.X:5000
   ```
   (Replace X with your computer's IP)

4. **Check Firewall:**
   - Windows: Allow Python through Windows Firewall
   - Linux: `sudo ufw allow 5000`

---

### 5. Login Problems

**Error:** `Invalid username or password`

**Solution:**

1. **Reset admin password:**
   ```bash
   python seed_admin.py
   ```
   This will recreate the admin user with default password: `admin123`

2. **Check database:**
   ```bash
   # Open SQLite database
   sqlite3 instance/isp_billing.db
   
   # Check users
   SELECT * FROM user;
   
   # Exit
   .quit
   ```

---

### 6. Port Already in Use

**Error:** `Address already in use: 5000`

**Solution:**

1. **Find process using port 5000:**
   - Windows:
   ```bash
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   ```
   
   - Linux/Mac:
   ```bash
   lsof -i :5000
   kill -9 <PID>
   ```

2. **Use different port:**
   ```bash
   python app.py
   # Edit app.py and change port to 5001
   ```

---

### 7. Module Not Found Errors

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**

1. **Make sure you're in the right directory:**
   ```bash
   cd path/to/ISP_Management_System
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Use virtual environment (recommended):**
   ```bash
   # Create venv
   python -m venv venv
   
   # Activate
   # Windows:
   venv\Scripts\activate
   
   # Linux/Mac:
   source venv/bin/activate
   
   # Install
   pip install -r requirements.txt
   ```

---

### 8. CSS/Styling Not Loading

**Problem:** Page loads pero walang styling

**Solution:**

1. **Check static files:**
   - Make sure `static/` folder exists
   - Check browser console for 404 errors

2. **Clear browser cache:**
   - Press Ctrl+Shift+R (hard refresh)
   - Or clear browser cache

3. **Check templates:**
   - Verify `templates/base.html` has Tailwind CDN link

---

### 9. Slow Performance

**Problem:** System is slow or laggy

**Possible Solutions:**

1. **Database growing too large:**
   ```bash
   # Backup first
   cp instance/isp_billing.db instance/isp_billing.db.backup
   
   # Vacuum database
   sqlite3 instance/isp_billing.db "VACUUM;"
   ```

2. **Too many clients:**
   - Consider pagination (already implemented)
   - Archive old records

3. **Mikrotik connection slow:**
   - Check network latency
   - Reduce API calls frequency

---

### 10. Receipt Printing Issues

**Problem:** Receipt not printing correctly

**Solutions:**

1. **Check printer settings:**
   - Set paper size to 80mm (thermal printer)
   - Portrait orientation

2. **Browser print settings:**
   - Remove headers/footers
   - Set margins to minimum
   - Scale: 100%

3. **Use Print Preview first:**
   - Check layout before printing
   - Adjust if needed

---

## Getting Help

Kung hindi pa rin gumagana after trying these solutions:

1. **Check log files:**
   - Look for error messages in terminal
   - Check `logs/` folder if it exists

2. **Test individual components:**
   ```bash
   # Test database
   python -c "from app import create_app; app = create_app(); print('DB OK')"
   
   # Test Mikrotik connection
   python -c "from services.mikrotik_service import MikrotikService; print('Mikrotik OK')"
   ```

3. **Restart everything:**
   - Stop the application (Ctrl+C)
   - Close terminal
   - Restart computer if needed
   - Run `start.bat` or `start.sh` again

---

## Prevention Tips

1. **Always backup database before major changes:**
   ```bash
   cp instance/isp_billing.db instance/isp_billing.db.backup
   ```

2. **Keep dependencies updated:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Use virtual environment:**
   - Prevents conflicts with other Python projects

4. **Regular maintenance:**
   - Clean old logs
   - Archive old billing records
   - Vacuum database monthly

---

## Still Having Issues?

Check these files for more information:
- `QUICK_START.md` - Basic setup
- `SETUP_GUIDE.md` - Detailed setup
- `DATABASE_SETUP.md` - Database issues
- `README.md` - General information
