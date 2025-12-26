# Quick Start: Deploy to Render

This is a quick reference guide. For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Pre-Deployment Checklist

- [ ] Code is committed and pushed to GitHub/GitLab
- [ ] All environment variables are documented (see [ENV_VARIABLES.md](ENV_VARIABLES.md))
- [ ] Generated a new SECRET_KEY for production
- [ ] Updated Google OAuth2 redirect URIs (if using social auth)

## Deployment Steps

### 1. Create PostgreSQL Database
- Render Dashboard → New + → PostgreSQL
- Name: `evara-postgres`
- Note the connection details

### 2. Create Web Service
- Render Dashboard → New + → Web Service
- Connect your repository
- Configure:
  - **Build Command**: `./build.sh`
  - **Start Command**: `gunicorn Evara.wsgi:application --bind 0.0.0.0:$PORT`
  - **Environment**: Python 3
  - **Python Version**: 3.12.0

### 3. Set Environment Variables
Add these in the Environment tab:
```
SECRET_KEY=<your-generated-key>
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=<your-key>
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=<your-secret>
```

Link your PostgreSQL database (this auto-sets DB_* variables).

### 4. Deploy
- Click "Create Web Service"
- Wait for build to complete
- Check logs for errors

### 5. Post-Deployment
- Run migrations in Shell: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
- Test your application

## Common Issues

**Build fails?** Check build logs, verify build.sh is executable

**Static files not loading?** Check collectstatic ran in build logs

**Database error?** Verify database is linked and credentials are correct

**500 error?** Check application logs, verify SECRET_KEY and ALLOWED_HOSTS

## Important Notes

- Free tier spins down after 15 minutes of inactivity
- Media files need cloud storage for production (current setup only works in DEBUG)
- SSL is automatic on Render
- Database backups are automatic

For detailed information, see [DEPLOYMENT.md](DEPLOYMENT.md).

