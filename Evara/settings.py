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

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

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
