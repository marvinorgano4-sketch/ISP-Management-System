# 🔄 Restart Instructions

## Ano ang Ginawa:

✅ Created `.env` file with Firebase configuration
✅ Updated `app.py` to make Firebase optional
✅ Firebase credentials file detected: `firebase-credentials.json`

## Paano I-restart:

### Step 1: Stop the Current Server

Sa terminal/command prompt:
1. Press **Ctrl + C** to stop the server
2. Wait for it to fully stop

### Step 2: Restart the Application

**Option A: Using start.bat (Recommended)**
```bash
start.bat
```

**Option B: Manual**
```bash
python app.py
```

### Step 3: Check if Working

1. Open browser: http://localhost:5000
2. Login: admin / admin123
3. Should work now! 🎉

## What's Fixed:

- ✅ Firebase credentials path configured
- ✅ Environment variables loaded from `.env`
- ✅ Mikrotik IP updated to 192.168.10.5
- ✅ System will work with or without Firebase

## If Still Having Issues:

### Check 1: Firebase Credentials File
```bash
# Should exist
dir firebase-credentials.json
```

### Check 2: .env File
```bash
# Should exist
dir .env
```

### Check 3: Restart Terminal
- Close the terminal completely
- Open a new terminal
- Run `start.bat` again

## Current Configuration:

**Mikrotik:**
- IP: 192.168.10.5
- User: admin
- Pass: adminTaboo

**Firebase:**
- Credentials: firebase-credentials.json
- Project ID: isp-billing-fadb0

**Database:**
- SQLite: instance/isp_billing.db
- Firebase: Optional (cloud backup)

---

**Ready!** Just restart the server and it should work! 🚀
