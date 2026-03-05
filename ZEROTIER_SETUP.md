# ZeroTier Setup Guide

## Ano ang ZeroTier?

Ang ZeroTier ay isang virtual private network (VPN) service na nagbibigay ng secure remote access sa iyong ISP Billing System kahit saan ka naroroon. Parang naka-connect ka sa local network kahit malayo ka.

## Step 1: Install ZeroTier sa Server

### Windows Server:
1. Download ZeroTier One: https://www.zerotier.com/download/
2. Run the installer
3. Install as Administrator
4. ZeroTier icon will appear sa system tray

### Linux Server:
```bash
curl -s https://install.zerotier.com | sudo bash
```

## Step 2: Create ZeroTier Network

1. Go to https://my.zerotier.com
2. Sign up or login
3. Click "Create A Network"
4. Copy ang **Network ID** (16-character code like: a0cbf4b62a1234567)
5. Click sa network name para i-configure

## Step 3: Configure Network Settings

Sa network configuration page:

1. **Access Control**: Set to "Private" (manual authorization required)
2. **IPv4 Auto-Assign**: Enable (automatic IP assignment)
3. **IPv6 Auto-Assign**: Optional
4. **Managed Routes**: Leave default

## Step 4: Join Server to Network

### Windows:
1. Right-click ZeroTier icon sa system tray
2. Click "Join Network"
3. Enter ang Network ID
4. Click "Join"

### Linux:
```bash
sudo zerotier-cli join [NETWORK_ID]
```

## Step 5: Authorize Server

1. Go back to https://my.zerotier.com
2. Click sa network
3. Scroll down to "Members" section
4. Find ang server (may checkmark sa "Online")
5. Check ang "Auth?" checkbox para i-authorize
6. Copy ang **Managed IP** (example: 10.147.17.1)

## Step 6: Verify Connection

### Windows:
```powershell
zerotier-cli listnetworks
```

### Linux:
```bash
sudo zerotier-cli listnetworks
```

Expected output:
```
200 listnetworks <network_id> <name> <mac> <status> OK <type> <dev> <ZT assigned ips>
```

## Step 7: Configure Flask App

Update `.env` file:
```bash
ZEROTIER_NETWORK_ID=a0cbf4b62a1234567
ZEROTIER_VIRTUAL_IP=10.147.17.1
```

## Step 8: Setup Client Devices

Para ma-access ang billing system from other devices:

1. Install ZeroTier One sa client device (laptop, desktop, mobile)
2. Join the same Network ID
3. Authorize ang device sa ZeroTier Central
4. Wait for virtual IP assignment
5. Access billing system: `http://[SERVER_VIRTUAL_IP]:5000`

Example: `http://10.147.17.1:5000`

## Troubleshooting

### Problem: "Cannot connect to network"
**Solution:**
- Check internet connection
- Verify Network ID is correct
- Check if device is authorized sa ZeroTier Central

### Problem: "No virtual IP assigned"
**Solution:**
- Wait 30 seconds for IP assignment
- Check if IPv4 Auto-Assign is enabled sa network settings
- Restart ZeroTier service

### Problem: "Cannot access Flask app via ZeroTier IP"
**Solution:**
- Verify Flask is running: `python app.py`
- Check if Flask is binding to 0.0.0.0 (not 127.0.0.1)
- Check firewall settings
- Verify ZeroTier connection: `zerotier-cli listnetworks`

## Security Best Practices

1. ✅ Use "Private" network (not Public)
2. ✅ Manually authorize each device
3. ✅ Regularly review authorized devices
4. ✅ Remove unused devices immediately
5. ✅ Use strong passwords for ZeroTier account
6. ✅ Enable 2FA sa ZeroTier account

## Next Steps

After ZeroTier setup:
1. Proceed to Firebase setup (FIREBASE_SETUP.md)
2. Run data migration (MIGRATION_GUIDE.md)
3. Test remote access

## Support

- ZeroTier Documentation: https://docs.zerotier.com
- ZeroTier Community: https://discuss.zerotier.com
