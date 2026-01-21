from pathlib import Path
import os
from decouple import config  # Importing decouple to use config()
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load sensitive settings from the .env file
# Fallback to os.environ for production (Render) or config for local development
SECRET_KEY = os.environ.get('SECRET_KEY', config('SECRET_KEY', default='django-insecure-temp-key-change-in-production'))

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG can be set via environment variable (string 'True'/'False' or boolean)
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

# ALLOWED_HOSTS can be set via environment variable (comma-separated list)
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',')]

# Django sites framework - Required for django-allauth
SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary',
    'cloudinary_storage',  # Must come before staticfiles
    'django.contrib.staticfiles',
    'allauth',
    'django.contrib.sites',
    'social_django',
    'Home',
    'UserAuth',
    'Shop',
    'Account',
    'Adminauth',
    'Categories',
    'Products',
    'Cart',
    'Order',
    'Wishlist',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'Evara.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'Cart.context_processors.cart_item_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'Evara.wsgi.application'

# Database configuration
# Use environment variables from Docker if available, otherwise use .env file
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    # Render usually provides DATABASE_URL when the DB is linked
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', config('DB_NAME', default='evara')),
            'USER': os.environ.get('DB_USER', config('DB_USER', default='nihal')),
            'PASSWORD': os.environ.get('DB_PASSWORD', config('DB_PASSWORD', default='')),
            'HOST': os.environ.get('DB_HOST', config('DB_HOST', default='localhost')),
            'PORT': os.environ.get('DB_PORT', config('DB_PORT', default='5432')),
        }
    }

# Cloudinary Configuration
# Try to get from environment variables first, then fallback to config() from decouple
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME') or config('CLOUDINARY_CLOUD_NAME', default='')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY') or config('CLOUDINARY_API_KEY', default='')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET') or config('CLOUDINARY_API_SECRET', default='')

# Only configure Cloudinary if credentials are provided
if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        
        # Configure Cloudinary SDK
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )
        
        # Cloudinary Storage Settings - Required dictionary configuration
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
            'API_KEY': CLOUDINARY_API_KEY,
            'API_SECRET': CLOUDINARY_API_SECRET,
        }
        
        # Use Cloudinary for media files
        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
        
        # Verify Cloudinary is working
        print(f"✓ Cloudinary configured successfully - Cloud Name: {CLOUDINARY_CLOUD_NAME}")
        print(f"✓ Using storage: {DEFAULT_FILE_STORAGE}")
    except ImportError as e:
        print(f"✗ Warning: Cloudinary packages not installed: {e}")
        print("Install with: pip install cloudinary django-cloudinary-storage")
        DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    except Exception as e:
        print(f"✗ Warning: Cloudinary configuration failed: {e}")
        import traceback
        print(traceback.format_exc())
        # Fallback to default storage if Cloudinary fails
        DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    print("✗ Warning: Cloudinary credentials not found. Using default file storage.")
    print(f"  CLOUDINARY_CLOUD_NAME: {'SET' if CLOUDINARY_CLOUD_NAME else 'NOT SET'}")
    print(f"  CLOUDINARY_API_KEY: {'SET' if CLOUDINARY_API_KEY else 'NOT SET'}")
    print(f"  CLOUDINARY_API_SECRET: {'SET' if CLOUDINARY_API_SECRET else 'NOT SET'}")
    print("  Please set these in your .env file or environment variables.")
    # Fallback to default storage if credentials are missing
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# MEDIA_URL and MEDIA_ROOT - Cloudinary handles actual storage, but keep URL for compatibility
MEDIA_URL = '/media/'
# MEDIA_ROOT is not needed when using Cloudinary, but kept for backward compatibility
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Final verification of storage configuration (for debugging)
print("\n" + "="*60)
print("STORAGE CONFIGURATION SUMMARY:")
print("="*60)
print(f"DEFAULT_FILE_STORAGE: {DEFAULT_FILE_STORAGE}")
if 'cloudinary' in DEFAULT_FILE_STORAGE.lower():
    print("✓ Cloudinary storage is ACTIVE")
    print(f"  Cloud Name: {CLOUDINARY_CLOUD_NAME}")
    print("  New image uploads will be stored in Cloudinary")
    print("  Image URLs will be: https://res.cloudinary.com/...")
else:
    print("✗ Using LOCAL file storage (Cloudinary not configured)")
    print("  Image URLs will be: /media/...")
    print("  To enable Cloudinary, set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET")
print("="*60 + "\n")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Email configuration (SendGrid SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# SendGrid SMTP: username is literal "apikey"; password is your SendGrid API key
EMAIL_HOST_USER = os.environ.get("SENDGRID_USERNAME", "apikey")
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_API_KEY", "")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")

EMAIL_TIMEOUT = 10

# SendGrid Web API key (for HTTP-based sending, not SMTP)
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Social authentication settings
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', default='')  
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', default='') 

LOGIN_URL = 'userlogin'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_URL = 'userlogout'
LOGOUT_REDIRECT_URL = 'userlogin'

SOCIAL_AUTH_URL_NAMESPACE = 'social'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'social_core': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Render handles SSL termination
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
