# Paano Gamitin ang ISP Billing System

## Unang Beses na Gagamitin

### Step 1: I-install ang System

**Pinakamadali:**
```bash
# Windows - double click lang
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

**Manual:**
```bash
pip install -r requirements.txt
flask db upgrade
python seed_admin.py
python app.py
```

### Step 2: Buksan sa Browser

Pumunta sa: **http://localhost:5000**

### Step 3: Mag-login

```
Username: admin
Password: admin123
```

---

## Pag-gamit ng System

### Dashboard

Pagbukas mo, makikita mo ang:
- Total Clients
- Active Connections (real-time from Mikrotik)
- Total Billings
- Total Payments
- Recent activities

### 1. Magdagdag ng Cliente

1. Click **"Clients"** sa menu
2. Click **"Add New Client"**
3. Punan ang form:
   - Full Name
   - Address
   - Contact Number
   - Email (optional)
   - PPPoE Username (para sa Mikrotik)
   - PPPoE Password
   - Plan Amount
   - Installation Date
   - Status (Active/Inactive)

4. Click **"Save"**

**Automatic:** Kapag nag-save, automatic na gagawa ng PPPoE user sa Mikrotik!

### 2. Tingnan ang Clients

1. Click **"Clients"** sa menu
2. Makikita mo lahat ng clients
3. May search function para madaling hanapin
4. Click sa client name para makita ang details

**Sa Client Details makikita mo:**
- Personal information
- Connection status (Online/Offline from Mikrotik)
- Billing history
- Payment history
- Recent activities

### 3. Gumawa ng Billing

**Option 1: Generate All (Recommended)**
1. Click **"Billing"** sa menu
2. Click **"Generate Monthly Bills"**
3. Piliin ang month at year
4. Click **"Generate"**
5. Automatic na gagawa ng bills para sa lahat ng active clients

**Option 2: Manual per Client**
1. Go to Client details
2. Click **"Create Bill"**
3. Punan ang details
4. Click **"Save"**

### 4. Mag-record ng Payment

**Option 1: From Billing List**
1. Click **"Billing"** sa menu
2. Hanapin ang bill
3. Click **"Record Payment"**
4. Punan ang:
   - Amount Paid
   - Payment Method (Cash/GCash/Bank Transfer)
   - Payment Date
   - Reference Number (optional)
5. Click **"Save"**

**Option 2: From Payments Menu**
1. Click **"Payments"** sa menu
2. Click **"Record New Payment"**
3. Piliin ang client
4. Piliin ang billing
5. Punan ang details
6. Click **"Save"**

### 5. Mag-print ng Receipt

**Automatic after payment:**
- Pagkatapos mag-record ng payment, automatic na lalabas ang receipt
- Click **"Print"** para i-print

**Manual:**
1. Click **"Payments"** sa menu
2. Hanapin ang payment
3. Click **"View Receipt"**
4. Click **"Print"**

**Print Settings:**
- Paper: 80mm thermal paper
- Orientation: Portrait
- Margins: Minimum
- Remove headers/footers

---

## Tips at Tricks

### Search Function

Lahat ng lists may search:
- Type lang sa search box
- Real-time ang search
- Pwede search by name, username, contact, etc.

### Filters

Sa Billing at Payments:
- Filter by status (Paid/Unpaid/Overdue)
- Filter by date range
- Filter by client

### Keyboard Shortcuts

- **Ctrl + S** - Save form (sa mga forms)
- **Esc** - Close modal/dialog
- **Ctrl + P** - Print (sa receipt page)

### Connection Status

Sa Client list:
- **Green dot** = Online sa Mikrotik
- **Red dot** = Offline
- **Gray dot** = Unknown/Error

---

## Common Tasks

### Baguhin ang Client Status

1. Go to Client details
2. Click **"Edit"**
3. Change status to Active/Inactive
4. Click **"Save"**

**Note:** Pag inactive, hindi kasama sa automatic billing generation

### Baguhin ang Plan Amount

1. Go to Client details
2. Click **"Edit"**
3. Update ang Plan Amount
4. Click **"Save"**

**Note:** Ang bagong amount ay gagamitin sa susunod na billing

### Hanapin ang Overdue Bills

1. Click **"Billing"** sa menu
2. Filter by Status: **"Overdue"**
3. Makikita lahat ng overdue bills
4. Pwede mag-send ng reminder (future feature)

### Check Payment History

**Per Client:**
1. Go to Client details
2. Scroll down to Payment History section

**All Payments:**
1. Click **"Payments"** sa menu
2. Makikita lahat ng payments
3. Filter by date range kung gusto

### Monthly Reports

**Dashboard:**
- Makikita ang summary ng current month
- Total collections
- Outstanding balance
- Active clients

**Detailed Reports:**
1. Click **"Billing"** o **"Payments"**
2. Filter by date range
3. Export to Excel (future feature)

---

## Mikrotik Integration

### Automatic PPPoE Creation

Kapag nag-add ng client:
1. Automatic na gagawa ng PPPoE user sa Mikrotik
2. Username at password from client form
3. Profile: default (pwede baguhin sa Mikrotik)

### Real-time Connection Status

- Dashboard shows active connections
- Client list shows online/offline status
- Updates every page refresh

### Manual Sync

Kung may problema sa connection status:
1. Refresh ang page
2. Check Mikrotik connection sa settings
3. Verify API is enabled sa Mikrotik

---

## Security Tips

### Change Admin Password

1. Login as admin
2. Go to Settings (future feature)
3. Change password
4. Use strong password

**Temporary:** Edit database directly:
```bash
python seed_admin.py
# Then change password in code
```

### Backup Database

**Regular Backup:**
```bash
# Copy database file
cp instance/isp_billing.db backups/isp_billing_$(date +%Y%m%d).db
```

**Before Major Changes:**
```bash
cp instance/isp_billing.db instance/isp_billing.db.backup
```

### Secure Mikrotik Access

1. Use strong password sa Mikrotik
2. Limit API access to specific IPs
3. Enable firewall rules
4. Regular firmware updates

---

## Maintenance

### Daily

- Check dashboard for overview
- Process payments
- Generate receipts

### Weekly

- Review overdue bills
- Check connection status
- Backup database

### Monthly

- Generate monthly bills
- Review payment reports
- Archive old records (future feature)
- Update client information

---

## Troubleshooting

Kung may problema, check:
1. **TROUBLESHOOTING.md** - Common problems at solutions
2. **QUICK_START.md** - Setup issues
3. Terminal/console - Error messages

**Quick Fixes:**
- Restart application (Ctrl+C then run again)
- Refresh browser (Ctrl+Shift+R)
- Check Mikrotik connection
- Verify database exists

---

## Future Features (Coming Soon)

- [ ] SMS notifications for overdue bills
- [ ] Email receipts
- [ ] Excel export for reports
- [ ] Multiple user accounts with roles
- [ ] Client portal (self-service)
- [ ] Automated billing reminders
- [ ] Payment gateway integration (GCash, PayMaya)
- [ ] Mobile app
- [ ] ZeroTier remote access
- [ ] Firebase cloud database

---

## Need Help?

**Documentation:**
- `QUICK_START.md` - Quick setup guide
- `TROUBLESHOOTING.md` - Problem solving
- `SETUP_GUIDE.md` - Detailed setup
- `README.md` - System overview

**Support:**
- Check error messages sa terminal
- Review log files
- Test Mikrotik connection
- Verify database integrity

---

**L SECURITY ISP BILLING SYSTEM**
Version 1.0
