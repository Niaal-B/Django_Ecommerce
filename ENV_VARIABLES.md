# Environment Variables Reference

This document lists all environment variables required for deployment on Render.

## Required Variables

Copy these variables and set them in your Render dashboard under your web service's "Environment" section.

### Django Core Settings

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
```

**To generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Database Configuration

These are automatically set by Render when you link a PostgreSQL database. However, if you need to set them manually:

```
DB_HOST=your-database-host-from-render
DB_PORT=5432
DB_NAME=evara
DB_USER=your-database-user
DB_PASSWORD=your-database-password
```

### Email Configuration

```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

**Note**: For Gmail, you need to create an App Password:
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate app password
4. Use this password, not your regular Gmail password

### Google OAuth2 (Optional - if using social authentication)

```
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-oauth2-client-id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-oauth2-client-secret
```

**To get these:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Configure OAuth consent screen
6. Create OAuth 2.0 Client ID for Web application
7. Add authorized redirect URI: `https://your-app-name.onrender.com/social-auth/complete/google-oauth2/`

### Python Version

```
PYTHON_VERSION=3.12.0
```

## Setting Variables in Render

1. Go to your web service in Render dashboard
2. Click on "Environment" tab
3. Click "Add Environment Variable"
4. Enter the key and value
5. Click "Save Changes"
6. Render will automatically redeploy your service

## Important Notes

- Never commit `.env` files or environment variables to git
- Keep your SECRET_KEY secure and unique for production
- Update ALLOWED_HOSTS to match your Render domain
- For Render's free tier, the database credentials are automatically provided when you link the database
- All string values should be entered as-is (no quotes needed in Render's interface)

