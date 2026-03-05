# How to Add the AZADOOE ETN Logo

## Quick Steps

1. **Save the logo image**
   - Right-click on the AZADOOE ETN logo image
   - Save as: `logo.png`

2. **Copy to the correct folder**
   - Copy `logo.png` to: `static/images/logo.png`
   - Full path: `ISP_Management_System/static/images/logo.png`

3. **Refresh the browser**
   - Open or refresh the login page
   - The logo should now appear!

## Logo Specifications

**Recommended:**
- Format: PNG with transparent background
- Size: 400x150 pixels (or similar ratio)
- Max height: 100px (will auto-resize)

**Acceptable:**
- JPG/JPEG (but PNG is better)
- Any size (will auto-scale)

## Where the Logo Appears

1. **Login Page**
   - Centered at the top
   - Above "Billing System" text
   - Height: ~96px (24 in Tailwind = 96px)

2. **Navigation Bar (All Pages)**
   - Top left corner
   - Next to "ANDODNAK ISP" text
   - Height: ~40px (10 in Tailwind = 40px)

## Fallback Behavior

If the logo file is missing or fails to load:
- **Login page**: Shows "ANDODNAK ISP" text instead
- **Navigation bar**: Logo space is hidden, only text shows

This ensures the system works even without the logo file.

## Testing

1. **With logo:**
   ```
   static/images/logo.png exists
   → Logo displays on login and navigation
   ```

2. **Without logo:**
   ```
   static/images/logo.png missing
   → Text fallback displays instead
   ```

## Troubleshooting

**Logo not showing?**

1. Check file location:
   ```
   static/images/logo.png
   ```

2. Check filename (case-sensitive):
   - Correct: `logo.png`
   - Wrong: `Logo.png`, `LOGO.PNG`, `logo.PNG`

3. Check file permissions:
   - File should be readable
   - Windows: Right-click → Properties → Security

4. Clear browser cache:
   - Press Ctrl+Shift+R (hard refresh)
   - Or clear browser cache completely

5. Check browser console:
   - Press F12
   - Look for 404 errors
   - Check the exact path being requested

**Logo too big/small?**

Edit the template files:
- Login page: `templates/login.html` (line with `h-24`)
- Navigation: `templates/base.html` (line with `h-10`)

Change the height class:
- `h-8` = 32px (small)
- `h-10` = 40px (medium)
- `h-12` = 48px (large)
- `h-16` = 64px (extra large)
- `h-24` = 96px (very large)

## Current Branding

✅ Company Name: **ANDODNAK ISP**
✅ Tagline: **Network and Data Solution**
✅ Developer Credit: **Marvin Organo**

All branding has been updated in:
- Login page
- Navigation bar
- Footer (all pages)
- Receipt template

## File Locations

```
ISP_Management_System/
├── static/
│   └── images/
│       ├── logo.png              ← PUT LOGO HERE
│       └── LOGO_INSTRUCTIONS.txt
├── templates/
│   ├── login.html               ← Updated with logo
│   ├── base.html                ← Updated with logo
│   └── receipts/
│       └── receipt.html         ← Updated branding
└── HOW_TO_ADD_LOGO.md          ← This file
```

---

**Need help?** Check `TROUBLESHOOTING.md` for more solutions.
