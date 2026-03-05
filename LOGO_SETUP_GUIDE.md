# 🎨 Logo Setup Guide - AZADOOE ETN

## ✅ Tapos na ang Branding Update!

Lahat ng pages ay updated na with:
- ✅ Company Name: **ANDODNAK ISP**
- ✅ Tagline: **Network and Data Solution**
- ✅ Developer: **Marvin Organo**

## 📸 Paano Ilagay ang Logo

### Step 1: Save the Logo Image

1. Right-click sa AZADOOE ETN logo image
2. Click "Save image as..."
3. Save as: **`logo.png`**
4. Remember kung saan mo na-save

### Step 2: Copy to Project Folder

**Windows:**
```
1. Open File Explorer
2. Navigate to: ISP_Management_System\static\images\
3. Paste ang logo.png dito
```

**Full path dapat:**
```
C:\Users\REYMARK\Desktop\ISP_Management_System\static\images\logo.png
```

### Step 3: Refresh Browser

1. Open or refresh ang login page
2. Logo should appear na! 🎉

## 🖼️ Logo Specifications

**Recommended:**
- **Format:** PNG with transparent background
- **Size:** 400x150 pixels (or similar ratio)
- **File size:** Less than 500KB

**Acceptable:**
- JPG/JPEG (but PNG is better for quality)
- Any size (will auto-resize)

## 📍 Saan Lalabas ang Logo

### 1. Login Page
```
┌─────────────────────────────┐
│                             │
│    [AZADOOE ETN LOGO]      │  ← Dito (centered, malaki)
│                             │
│      Billing System         │
│                             │
│    [Login Form]             │
└─────────────────────────────┘
```

### 2. Navigation Bar (All Pages)
```
┌────────────────────────────────────────────┐
│ [LOGO] ANDODNAK ISP    Dashboard  Logout  │  ← Dito (left side, maliit)
│        Network and Data Solution           │
└────────────────────────────────────────────┘
```

### 3. Footer (All Pages)
```
┌────────────────────────────────────────────┐
│     © 2024 ANDODNAK ISP. All rights reserved.│
│          Developer: Marvin Organo          │  ← Developer credit
└────────────────────────────────────────────┘
```

## 🔍 Paano I-check kung Tama

### Test 1: Login Page
1. Open: http://localhost:5000
2. Dapat makita ang logo sa taas
3. Below logo: "Billing System"

### Test 2: Dashboard
1. Login using admin/admin123
2. Tingnan ang top-left corner
3. Dapat may logo + "ANDODNAK ISP" text

### Test 3: Footer
1. Scroll down sa any page
2. Dapat makita: "Developer: Marvin Organo"

## ❌ Troubleshooting

### Logo hindi lumalabas?

**Check 1: File location**
```bash
# Windows - check if file exists
dir static\images\logo.png

# Should show: logo.png
```

**Check 2: Filename (case-sensitive!)**
- ✅ Correct: `logo.png`
- ❌ Wrong: `Logo.png`, `LOGO.PNG`, `logo.PNG`

**Check 3: File permissions**
- Right-click logo.png
- Properties → Security
- Make sure "Read" is allowed

**Check 4: Browser cache**
- Press `Ctrl + Shift + R` (hard refresh)
- Or clear browser cache completely

**Check 5: Browser console**
- Press `F12`
- Go to Console tab
- Look for errors like "404 Not Found"

### Logo masyadong malaki/maliit?

**Para sa Login Page:**
1. Open: `templates/login.html`
2. Find: `class="mx-auto h-24 w-auto"`
3. Change `h-24` to:
   - `h-16` = smaller (64px)
   - `h-20` = medium (80px)
   - `h-24` = current (96px)
   - `h-32` = larger (128px)

**Para sa Navigation:**
1. Open: `templates/base.html`
2. Find: `class="h-10 w-auto"`
3. Change `h-10` to:
   - `h-8` = smaller (32px)
   - `h-10` = current (40px)
   - `h-12` = larger (48px)

## 🎯 Kung Walang Logo File

**Don't worry!** System will still work:
- Login page: Shows "ANDODNAK ISP" text instead
- Navigation: Shows text only
- Everything functions normally

Logo is optional pero mas maganda kung meron! 😊

## 📁 File Structure

```
ISP_Management_System/
├── static/
│   └── images/
│       ├── logo.png              ← ILAGAY DITO ANG LOGO
│       ├── LOGO_INSTRUCTIONS.txt
│       └── (other images)
├── templates/
│   ├── login.html               ← Logo code here
│   ├── base.html                ← Logo code here
│   └── receipts/
│       └── receipt.html         ← Branding updated
├── HOW_TO_ADD_LOGO.md          ← Detailed guide
├── BRANDING_UPDATE_SUMMARY.md  ← Technical details
└── LOGO_SETUP_GUIDE.md         ← This file
```

## ✨ What's Updated

### Templates Updated:
1. ✅ `templates/login.html` - Logo + branding
2. ✅ `templates/base.html` - Logo + navigation + footer
3. ✅ `templates/receipts/receipt.html` - Receipt branding

### Branding Changed:
- ✅ Company: L SECURITY ISP → **ANDODNAK ISP**
- ✅ Added: **Network and Data Solution**
- ✅ Added: **Developer: Marvin Organo**

### Logo Integration:
- ✅ Login page placeholder
- ✅ Navigation bar placeholder
- ✅ Automatic fallback to text
- ✅ Responsive design

## 🚀 Ready to Use!

**Current Status:**
- ✅ All branding updated
- ✅ Logo placeholders ready
- ✅ Developer credit added
- ⏳ Waiting for logo file

**Action Required:**
1. Save AZADOOE ETN logo as `logo.png`
2. Copy to `static/images/logo.png`
3. Refresh browser
4. Done! 🎉

---

## Quick Reference

**Logo File:**
- Name: `logo.png`
- Location: `static/images/logo.png`
- Format: PNG (recommended) or JPG
- Size: Any (will auto-resize)

**Company Info:**
- Name: ANDODNAK ISP
- Tagline: Network and Data Solution
- Developer: Marvin Organo

**Test URLs:**
- Login: http://localhost:5000
- Dashboard: http://localhost:5000 (after login)

---

**Need more help?** Check:
- `HOW_TO_ADD_LOGO.md` - Detailed instructions
- `BRANDING_UPDATE_SUMMARY.md` - Technical details
- `TROUBLESHOOTING.md` - Common problems

**ANDODNAK ISP - Network and Data Solution**
Developer: Marvin Organo
