# Firebase Setup Guide

## Ano ang Firebase Firestore?

Ang Firebase Firestore ay isang cloud-based NoSQL database na nag-store ng data sa cloud. Automatic backup, real-time sync, at accessible kahit saan.

## Step 1: Create Firebase Project

1. Go to https://console.firebase.google.com
2. Click "Add project" or "Create a project"
3. Enter project name: `isp-billing-system` (or any name you prefer)
4. Click "Continue"
5. Disable Google Analytics (optional, not needed for this project)
6. Click "Create project"
7. Wait for project creation (30 seconds)
8. Click "Continue"

## Step 2: Enable Firestore Database

1. Sa Firebase Console, click "Firestore Database" sa left sidebar
2. Click "Create database"
3. Select "Start in production mode"
4. Click "Next"
5. Select Cloud Firestore location: `asia-southeast1` (Singapore) or closest to you
6. Click "Enable"
7. Wait for database creation

## Step 3: Configure Security Rules

1. Sa Firestore Database page, click "Rules" tab
2. Replace the rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Deny all direct client access
    // Only Firebase Admin SDK can access
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

3. Click "Publish"

## Step 4: Generate Service Account Credentials

1. Click sa gear icon (⚙️) sa top-left, then "Project settings"
2. Click "Service accounts" tab
3. Click "Generate new private key"
4. Click "Generate key" sa popup
5. A JSON file will download (example: `isp-billing-system-firebase-adminsdk-xxxxx.json`)
6. **IMPORTANT:** Keep this file secure! Never commit to Git!

## Step 5: Setup Credentials sa Server

1. Rename the downloaded file to `firebase-credentials.json`
2. Move the file to your project root directory
3. Set file permissions (Linux/Mac):
   ```bash
   chmod 600 firebase-credentials.json
   ```

4. Update `.env` file:
   ```bash
   FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
   FIREBASE_PROJECT_ID=isp-billing-system
   ```

## Step 6: Verify Firebase Project ID

1. Sa Firebase Console, click "Project settings"
2. Copy ang "Project ID" (example: `isp-billing-system-12345`)
3. Update `.env` file with correct Project ID:
   ```bash
   FIREBASE_PROJECT_ID=isp-billing-system-12345
   ```

## Step 7: Install Firebase Admin SDK

```bash
pip install firebase-admin
```

## Step 8: Test Firebase Connection

Run the test script:
```bash
python test_firebase_connection.py
```

Expected output:
```
✓ Firebase initialized successfully
✓ Firestore client created
✓ Connection test passed
```

## Firestore Data Structure

Ang data ay organized sa collections:

```
firestore_root/
├── users/           # User accounts
├── clients/         # ISP customers
├── billings/        # Monthly bills
├── payments/        # Payment records
└── receipts/        # Payment receipts
```

## Security Best Practices

1. ✅ Never commit `firebase-credentials.json` to Git
2. ✅ Add to `.gitignore`:
   ```
   firebase-credentials.json
   *.json
   ```
3. ✅ Set file permissions to 600 (read/write owner only)
4. ✅ Use environment variables for sensitive config
5. ✅ Rotate service account keys every 90 days
6. ✅ Use production mode security rules
7. ✅ Monitor Firebase usage and billing

## Firestore Pricing

**Free Tier (Spark Plan):**
- 1 GB storage
- 50,000 reads/day
- 20,000 writes/day
- 20,000 deletes/day

**Paid Tier (Blaze Plan):**
- Pay as you go
- $0.18 per GB storage/month
- $0.06 per 100,000 reads
- $0.18 per 100,000 writes

**Recommendation:** Start with Free Tier, upgrade if needed.

## Monitoring Firebase Usage

1. Go to Firebase Console
2. Click "Usage and billing"
3. Monitor:
   - Document reads/writes
   - Storage usage
   - Network egress

## Troubleshooting

### Problem: "Permission denied" error
**Solution:**
- Check if security rules are set correctly
- Verify service account has Firestore permissions
- Check if credentials file path is correct

### Problem: "Project not found"
**Solution:**
- Verify FIREBASE_PROJECT_ID in .env matches Firebase Console
- Check if Firestore is enabled in the project

### Problem: "Credentials file not found"
**Solution:**
- Verify firebase-credentials.json exists in project root
- Check FIREBASE_CREDENTIALS_PATH in .env
- Verify file permissions (should be readable)

## Next Steps

After Firebase setup:
1. Run data migration: `python migrate_to_firebase.py`
2. Verify migration: Check Firestore Console for data
3. Test application with Firebase backend

## Support

- Firebase Documentation: https://firebase.google.com/docs/firestore
- Firebase Support: https://firebase.google.com/support
- Firestore Pricing: https://firebase.google.com/pricing
