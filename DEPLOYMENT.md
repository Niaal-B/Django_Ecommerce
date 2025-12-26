# Deployment Guide for Render

This guide will walk you through deploying your Django E-commerce application to Render.

## Prerequisites

1. A GitHub account (recommended) or GitLab account
2. A Render account (sign up at https://render.com)
3. All environment variables ready (see below)

## Step-by-Step Deployment Instructions

### Step 1: Prepare Your Code

1. **Commit all changes to git**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main  # or your branch name
   ```

### Step 2: Create a PostgreSQL Database on Render

1. Log in to your Render dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Configure the database:
   - **Name**: `evara-postgres` (or any name you prefer)
   - **Database**: `evara`
   - **User**: `evara_user` (or any username)
   - **Plan**: Choose based on your needs (Free tier available)
   - **Region**: Choose closest to your users
4. Click **"Create Database"**
5. **Important**: Copy the **Internal Database URL** (you'll use this later)

### Step 3: Set Up Environment Variables

Before deploying, gather all the required environment variables:

#### Required Environment Variables:

1. **SECRET_KEY**: Django secret key (generate a new one for production)
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **DEBUG**: Set to `False` for production

3. **ALLOWED_HOSTS**: Your Render app domain (e.g., `your-app-name.onrender.com`)

4. **Database Variables** (from Render PostgreSQL):
   - `DB_HOST`: From your database connection string
   - `DB_PORT`: Usually `5432`
   - `DB_NAME`: Database name (e.g., `evara`)
   - `DB_USER`: Database user
   - `DB_PASSWORD`: Database password

5. **Email Configuration**:
   - `EMAIL_HOST_USER`: Your Gmail address
   - `EMAIL_HOST_PASSWORD`: Gmail App Password (not your regular password)

6. **Google OAuth2** (if using social auth):
   - `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`: Google OAuth2 Client ID
   - `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`: Google OAuth2 Client Secret

### Step 4: Create a Web Service on Render

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub/GitLab repository
3. Configure the service:

   **Basic Settings:**
   - **Name**: `evara-django-app` (or any name)
   - **Environment**: `Python 3`
   - **Region**: Same as your database
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: Leave empty (if project is at repo root)

   **Build & Deploy:**
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn Evara.wsgi:application --bind 0.0.0.0:$PORT`

   **Environment Variables:**
   Add all the environment variables from Step 3:
   - `PYTHON_VERSION`: `3.12.0`
   - `SECRET_KEY`: (your generated secret key)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com` (will be set automatically by Render)
   - `DB_HOST`: (from your PostgreSQL connection)
   - `DB_PORT`: `5432`
   - `DB_NAME`: (from your PostgreSQL)
   - `DB_USER`: (from your PostgreSQL)
   - `DB_PASSWORD`: (from your PostgreSQL)
   - `EMAIL_HOST_USER`: (your email)
   - `EMAIL_HOST_PASSWORD`: (your email app password)
   - `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`: (if using)
   - `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`: (if using)

   **Alternative**: If you created a `render.yaml` file, you can use it for configuration (see below).

4. **Link the Database**:
   - In the "Environment" section, find "Link PostgreSQL Database"
   - Select your database created in Step 2
   - Render will automatically add the database environment variables

5. Click **"Create Web Service"**

### Step 5: Update Google OAuth2 Settings (if applicable)

If you're using Google OAuth2, update your Google Cloud Console settings:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Edit your OAuth2 client
4. Add authorized redirect URIs:
   - `https://your-app-name.onrender.com/social-auth/complete/google-oauth2/`
5. Save changes

### Step 6: Media Files Handling

**Important**: The current setup serves media files only in DEBUG mode. For production, you should use cloud storage:

**Option 1: Use Render's Persistent Disk** (for small projects)
- Add a persistent disk to your web service
- Mount it to `/media`
- Update settings to use the mounted path

**Option 2: Use Cloud Storage** (Recommended for production)
- Set up AWS S3, Cloudinary, or similar
- Install `django-storages`:
  ```bash
  pip install django-storages boto3
  ```
- Update `settings.py` to use cloud storage for media files

For now, media files uploaded in production will need to be handled separately.

### Step 7: Initial Deployment

1. Render will automatically start building your application
2. Wait for the build to complete (this may take 5-10 minutes)
3. Check the logs for any errors
4. Once deployed, your app will be available at: `https://your-app-name.onrender.com`

### Step 8: Run Initial Migrations

1. In Render dashboard, open your web service
2. Go to **"Shell"** tab
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser (if needed):
   ```bash
   python manage.py createsuperuser
   ```

### Step 9: Verify Deployment

1. Visit your app URL: `https://your-app-name.onrender.com`
2. Check if static files are loading correctly
3. Test admin panel: `https://your-app-name.onrender.com/admin`
4. Test main application functionality

## Troubleshooting

### Build Fails

1. Check build logs in Render dashboard
2. Common issues:
   - Missing dependencies in `requirements.txt`
   - Build script permissions (should be executable)
   - Python version mismatch

### Static Files Not Loading

1. Verify `collectstatic` ran successfully in build logs
2. Check that WhiteNoise middleware is properly configured
3. Ensure `STATIC_ROOT` is set correctly

### Database Connection Errors

1. Verify all database environment variables are set correctly
2. Check that the database is linked to your web service
3. Ensure database credentials are correct

### Media Files Not Uploading/Serving

1. Media files are only served in DEBUG mode
2. For production, set up cloud storage (see Step 6)
3. Or configure persistent disk for media files

### 500 Internal Server Errors

1. Check application logs in Render dashboard
2. Verify `SECRET_KEY` is set
3. Check `ALLOWED_HOSTS` includes your Render domain
4. Ensure `DEBUG=False` in production (check logs won't expose sensitive info)

## Using render.yaml (Alternative Method)

If you prefer configuration as code, you can use the provided `render.yaml` file:

1. Update `render.yaml` with your actual values
2. In Render dashboard, click **"New +"** → **"Blueprint"**
3. Connect your repository
4. Render will automatically detect and use `render.yaml`

**Note**: Update `ALLOWED_HOSTS` in `render.yaml` with your actual Render domain after deployment.

## Post-Deployment Checklist

- [ ] Application is accessible via public URL
- [ ] Static files are loading correctly
- [ ] Database migrations are applied
- [ ] Admin panel is accessible
- [ ] User registration/login works
- [ ] Email functionality works (test password reset)
- [ ] Google OAuth2 works (if configured)
- [ ] Media file uploads work (if cloud storage configured)
- [ ] SSL certificate is active (automatic on Render)

## Monitoring and Maintenance

1. **Logs**: Check application logs regularly in Render dashboard
2. **Database Backups**: Render automatically backs up PostgreSQL databases
3. **Updates**: Push to your connected branch to trigger automatic deployments
4. **Scaling**: Upgrade your plan if you need more resources

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [WhiteNoise Documentation](https://whitenoise.readthedocs.io/)

## Notes

- **Free Tier Limitations**: Render's free tier has limitations (spins down after inactivity, slower performance)
- **Database Backups**: Free tier databases are deleted after 90 days of inactivity
- **Media Storage**: Consider cloud storage for production media files
- **Environment Variables**: Keep sensitive variables secure, never commit them to git

