# Railway Deployment Guide - ISP Management System

## ✅ GitHub Repository Ready!
Ang iyong code ay naka-upload na sa:
**https://github.com/marvinorgano4-sketch/ISP-Management-System**

## 🚀 I-Deploy sa Railway (Step-by-Step)

### Step 1: Pumunta sa Railway
1. Buksan ang browser
2. Pumunta sa: **https://railway.app/**
3. Click "Login" (upper right)
4. Piliin "Login with GitHub"
5. I-authorize ang Railway na ma-access ang GitHub account mo

### Step 2: Create New Project
1. After mag-login, click "New Project" button
2. Piliin "Deploy from GitHub repo"
3. Hanapin at piliin ang **"ISP-Management-System"** repository
4. Click ang repository name

### Step 3: Automatic Deployment
Railway ay automatic na:
- Mag-detect ng Python project
- Mag-install ng dependencies from requirements.txt
- Mag-run ng Procfile (gunicorn app:app)
- Mag-deploy ng application

**Maghintay lang ng 2-5 minutes** habang nag-deploy.

### Step 4: I-configure ang Environment Variables
**IMPORTANTE**: Kailangan mo i-set ang mga environment variables para gumana ang system.

1. Sa Railway dashboard, click ang project mo
2. Click "Variables" tab sa left sidebar
3. Click "New Variable" button
4. I-add ang mga sumusunod ONE BY ONE:

```
SECRET_KEY=<i-generate mo using command sa baba>
MIKROTIK_HOST=192.168.10.5
MIKROTIK_USER=admin
MIKROTIK_PASSWORD=adminTaboo
```

**Para sa SECRET_KEY**, i-run mo ito sa terminal:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
I-copy ang output at i-paste bilang value ng SECRET_KEY.

4. After i-add ang lahat, click "Deploy" o maghintay ng automatic redeploy

### Step 5: I-access ang Deployed Application
1. Sa Railway dashboard, hanapin ang "Deployments" section
2. Click ang latest deployment
3. Hanapin ang "Public URL" o "Domain"
4. Click ang URL para ma-access ang application

**Example URL**: `https://isp-management-system-production.up.railway.app`

## 🔧 Troubleshooting

### Kung may error sa deployment:
1. Click "View Logs" sa Railway dashboard
2. Tingnan ang error message
3. I-fix ang issue sa local code
4. I-commit at i-push ulit sa GitHub:
   ```bash
   git add .
   git commit -m "Fix deployment issue"
   git push
   ```
5. Railway ay automatic na mag-redeploy

### Kung hindi ma-access ang Mikrotik:
- Siguraduhin na ang Railway server ay naka-connect sa network mo
- O i-configure ang ZeroTier para sa remote access (see ZEROTIER_SETUP.md)

### Kung may database error:
- Railway ay automatic na gumawa ng SQLite database
- Pero kung gusto mo ng persistent database, i-add ang Railway PostgreSQL:
  1. Click "New" → "Database" → "Add PostgreSQL"
  2. Railway ay automatic na mag-set ng DATABASE_URL

## 📝 Important Notes

1. **Free Tier Limits**:
   - Railway free tier: $5 credit per month
   - Enough para sa testing at small-scale deployment
   - Pag naubos, kailangan mag-upgrade o mag-deploy sa ibang platform

2. **Database Persistence**:
   - SQLite database ay naka-store sa Railway server
   - Pag nag-redeploy, mawawala ang data
   - Recommended: Gumamit ng PostgreSQL para sa production

3. **Mikrotik Access**:
   - Kailangan ng network connectivity between Railway at Mikrotik
   - Recommended: I-setup ang ZeroTier para sa secure remote access

## 🎉 Success!
Kapag nakita mo na ang login page, SUCCESS! Ang system mo ay online na at accessible kahit saan ka man.

Default admin credentials:
- Username: admin
- Password: admin123

**IMPORTANTE**: Palitan agad ang default password after first login!
