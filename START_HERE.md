# 🚀 START HERE - ANDODNAK ISP Billing System

## Mabilis na Simula (3 Steps Lang!)

### Step 1: Run the System

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### Step 2: Open Browser

Pumunta sa: **http://localhost:5000**

### Step 3: Login

```
Username: admin
Password: admin123
```

**TAPOS NA!** 🎉

---

## Ano ang Makikita Mo?

### Dashboard
- Total clients
- Active connections (from Mikrotik)
- Billing summary
- Payment summary

### Main Features
1. **Clients** - Manage customers
2. **Billing** - Generate monthly bills
3. **Payments** - Record payments
4. **Receipts** - Print receipts

---

## Current Configuration

### Mikrotik Settings
```
IP Address: 192.168.10.5
Username: admin
Password: adminTaboo
```

### System Access
```
Local: http://localhost:5000
Network: http://YOUR_IP:5000
```

---

## Quick Actions

### Add a Client
1. Click "Clients" → "Add New Client"
2. Fill in the form
3. Save
4. **Automatic PPPoE creation sa Mikrotik!**

### Generate Monthly Bills
1. Click "Billing" → "Generate Monthly Bills"
2. Select month and year
3. Generate
4. **Automatic bills for all active clients!**

### Record Payment
1. Click "Billing" → Find bill → "Record Payment"
2. Enter amount and payment method
3. Save
4. **Automatic receipt generation!**

### Print Receipt
1. After payment, click "Print"
2. Or go to "Payments" → View Receipt → Print

---

## Need Help?

### 📚 Documentation Files

**Para sa Setup:**
- `QUICK_START.md` - Detailed setup instructions
- `SETUP_GUIDE.md` - Complete setup guide
- `DATABASE_SETUP.md` - Database setup

**Para sa Paggamit:**
- `PAANO_GAMITIN.md` - **⭐ BASAHIN ITO!** Complete user guide
- `TROUBLESHOOTING.md` - Solutions sa common problems

**Para sa Advanced Features:**
- `ZEROTIER_SETUP.md` - Remote access setup
- `FIREBASE_SETUP.md` - Cloud database setup

### 🔧 Common Problems

**Hindi gumagana?**
1. Check if Python is installed: `python --version`
2. Check if dependencies are installed: `pip list`
3. Check if database exists: `ls instance/`
4. Read `TROUBLESHOOTING.md`

**Cannot connect to Mikrotik?**
1. Ping the Mikrotik: `ping 192.168.10.5`
2. Check if API is enabled sa Mikrotik
3. Verify username and password
4. Check firewall settings

**Cannot access from other devices?**
1. Make sure running with `0.0.0.0` host
2. Get your computer's IP: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
3. Access using: `http://YOUR_IP:5000`
4. Check firewall settings

---

## System Requirements

### Minimum
- Python 3.8 or higher
- 2GB RAM
- 100MB disk space
- Windows/Linux/Mac

### Recommended
- Python 3.10 or higher
- 4GB RAM
- 500MB disk space
- Stable internet connection

### Network
- Access to Mikrotik (192.168.10.5)
- Mikrotik API enabled
- Port 8728 accessible

---

## What's Working Now

✅ User authentication
✅ Client management (CRUD)
✅ Mikrotik PPPoE integration
✅ Real-time connection status
✅ Billing generation
✅ Payment recording
✅ Receipt printing
✅ Dashboard with statistics
✅ Search and filters
✅ Responsive design

---

## Coming Soon (In Progress)

🔄 ZeroTier remote access
🔄 Firebase cloud database
🔄 Data migration tool
🔄 Real-time updates
🔄 Advanced error handling
🔄 Performance monitoring

---

## Quick Reference

### File Structure
```
ISP_Management_System/
├── start.bat / start.sh    ← Run this!
├── app.py                  ← Main application
├── config.py               ← Configuration
├── requirements.txt        ← Dependencies
├── instance/
│   └── isp_billing.db     ← Database
├── models/                 ← Database models
├── services/               ← Business logic
├── routes/                 ← URL routes
├── templates/              ← HTML templates
└── tests/                  ← Test files
```

### Important Commands

**Start application:**
```bash
python app.py
```

**Setup database:**
```bash
flask db upgrade
python seed_admin.py
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run tests:**
```bash
pytest
```

---

## Next Steps

1. ✅ **Run the system** (you're here!)
2. 📖 **Read** `PAANO_GAMITIN.md` for detailed usage
3. 👥 **Add clients** and test the system
4. 💰 **Generate bills** and record payments
5. 🖨️ **Print receipts** and verify format
6. 🌐 **Setup remote access** (optional, see ZEROTIER_SETUP.md)
7. ☁️ **Migrate to cloud** (optional, see FIREBASE_SETUP.md)

---

## Support

**Kung may tanong o problema:**

1. Check `TROUBLESHOOTING.md` first
2. Read `PAANO_GAMITIN.md` for usage guide
3. Review error messages sa terminal
4. Check log files (if any)

**Before asking for help, provide:**
- Error message (screenshot or copy-paste)
- What you were trying to do
- System info (Windows/Linux/Mac, Python version)
- Mikrotik connection status

---

## Tips for Success

1. **Backup regularly** - Copy `instance/isp_billing.db` file
2. **Test first** - Try with 1-2 clients before adding all
3. **Verify Mikrotik** - Make sure connection works
4. **Keep updated** - Update dependencies regularly
5. **Read docs** - Check documentation when stuck

---

## Important Notes

⚠️ **Security:**
- Change admin password after first login
- Use strong passwords for Mikrotik
- Backup database regularly
- Don't expose to internet without proper security

⚠️ **Mikrotik:**
- Make sure API is enabled
- Verify IP address is correct
- Test connection before adding clients
- Keep Mikrotik firmware updated

⚠️ **Database:**
- SQLite is for single-user/small deployments
- For production with remote access, use Firebase
- Backup before major changes
- Vacuum database monthly

---

## Ready to Start?

1. Run `start.bat` (Windows) or `./start.sh` (Linux/Mac)
2. Open http://localhost:5000
3. Login with admin/admin123
4. Start adding clients!

**Good luck!** 🚀

---

**ANDODNAK ISP - BILLING SYSTEM**
*Network and Data Solution*
Developer: Marvin Organo
