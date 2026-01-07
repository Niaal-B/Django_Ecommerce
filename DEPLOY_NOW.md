# Quick Deployment Steps - Fix 500 Error

## What Was Fixed

✅ Added `SITE_ID = 1` (required for django-allauth)
✅ Fixed SECRET_KEY to work with environment variables
✅ Updated ALLOWED_HOSTS in render.yaml to `.onrender.com`
✅ Added production security settings
✅ Created setup_site.py script for Site configuration

## Deploy Now - 3 Steps

### Step 1: Commit and Push
```bash
git add .
git commit -m "Fix 500 error - add SITE_ID and production settings"
git push origin main
```

### Step 2: Set Environment Variable in Render

**Generate a new SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**In Render Dashboard:**
1. Go to your web service
2. Click "Environment" tab
3. Add/Update: `SECRET_KEY` = (paste the generated key)
4. Click "Save Changes"

Render will automatically redeploy after you push to GitHub.

### Step 3: Run Setup Script After Deploy

Once deployment is complete (watch the Logs):

1. Go to your web service → **Shell** tab
2. Run this command:
```bash
python setup_site.py
```

You should see: `Created Site: your-app-name.onrender.com` or `Updated Site: ...`

### Step 4: Test Your App

Visit your app URL: `https://your-app-name.onrender.com`

The 500 error should be gone! 🎉

## If Still Getting 500 Error

### Check Render Logs
Go to Logs tab and look for the error message. Common issues:

1. **"Site matching query does not exist"** → Run `python setup_site.py` in Shell
2. **"SECRET_KEY"** → Make sure SECRET_KEY is set in Environment variables
3. **Database error** → Verify database is linked to web service
4. **Migration error** → Run `python manage.py migrate` in Shell

### Manual Site Setup (Alternative to setup_site.py)

If setup_site.py doesn't work, run this in Render Shell:

```bash
python manage.py shell
```

Then:
```python
from django.contrib.sites.models import Site
import os
domain = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')
site = Site.objects.get_or_create(pk=1, defaults={'domain': domain, 'name': 'Evara'})
print(f"Site created/updated: {site}")
exit()
```

## Verify Everything Works

- [ ] Homepage loads without 500 error
- [ ] Static files (CSS/JS) are loading
- [ ] Admin panel accessible: `/admin`
- [ ] User login/registration works
- [ ] No errors in Render logs

## Summary of Files Changed

1. `Evara/settings.py` - Added SITE_ID, fixed SECRET_KEY, added security settings
2. `render.yaml` - Updated ALLOWED_HOSTS
3. `setup_site.py` - New script to configure Site object
4. Documentation files (RENDER_FIX.md, this file)

Good luck with your deployment! 🚀

