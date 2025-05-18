"""
Django settings for libis_communication project.
"""

from pathlib import Path
import os
from decouple import config, Csv

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


 
# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key-for-dev-only')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# Application definition
INSTALLED_APPS = [
    "unfold",  # <- Doit être en première position
    "unfold.contrib.filters",  # optional
    "unfold.contrib.forms",    # optional
    "unfold.contrib.inlines",  # optional
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    'widget_tweaks',
    'core',  # Votre application principale
]
# Unfold Admin Theme Configuration
UNFOLD = {


 

"DASHBOARD_CALLBACK": "core.dashboard.index",
    "SIDEBAR": {
            "dashboard": "core.dashboard.index",  # ✅ Remplacé par votre app
            "navigation": "core.navigation.get_navigation",  # ✅ Remplacé par votre app
        },





    "SITE_TITLE": "Libis Communication - Administration",
    "SITE_HEADER": "Libis Communication",
    "SITE_URL": "/",
     "STYLES": [
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    ],
    "SCRIPTS": [
        "https://cdn.jsdelivr.net/npm/@unfold/admin@latest/dist/js/unfold.js",
    ],
    "SITE_ICON": {
        "light": "https://github.com/like2300/libis_communication/blob/main/media/accueil/lbs.PNG?raw=true",  # Chemin relatif à static
        "dark": "https://github.com/like2300/libis_communication/blob/main/media/accueil/lbs.PNG?raw=true",
    },

    "SITE_LOGO": {
        "light": "https://github.com/like2300/libis_communication/blob/main/media/accueil/lbs.PNG?raw=true",  # Logo plus grand pour la page de login
        "dark": "https://github.com/like2300/libis_communication/blob/main/media/accueil/lbs.PNG?raw=true",
    },

     
    
    "SITE_SYMBOL": "settings",  # Symbole Material Icons pour le menu
    "COLORS": {
        "primary": {
            "50": "254 242 242",
            "100": "254 226 226",
            "200": "254 202 202",
            "300": "252 165 165",
            "400": "248 113 113",
            "500": "239 68 68",  # red-500 (plus visible que red-600)
            "600": "220 38 38",  # red-600 (couleur que vous demandez)
            "700": "185 28 28",
            "800": "153 27 27",
            "900": "127 29 29",
        },
    },
    "DARK_MODE": False,  # Mode sombre
    "LOGIN": {
        "image": "https://github.com/like2300/libis_communication/blob/main/media/accueil/lbs.PNG?raw=true",  # Image de fond pour la page de login
        "redirect_after": "/admin/",  # Redirection après connexion
    },
 
    
     "SHOW_HISTORY": True, 
      
}


 


UNFOLD["LOGIN"] = {
    "image": "images/login-bg.jpg",
    "color": "bg-purple-600",  # Couleur d'accent
    "title": "Libis Communication - Connexion Admin",
    "description": "Espace d'administration réservé au personnel autorisé",
}



 
# Add login/logout URLs (you have them but let's make them more visible)
# Paramètres d'authentification
LOGIN_URL = '/accounts/login/'  # URL de la page de connexion
LOGIN_REDIRECT_URL = 'edit_client_profile'  # Nom de l'URL de redirection après connexion
LOGOUT_REDIRECT_URL = 'home'  # Page après déconnexion
AUTH_USER_MODEL = 'core.User'  # Modèle utilisateur personnalisé
# URL de la page de connexion
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'libis_communication.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages', 
            ],
        },
    },
]


WSGI_APPLICATION = 'libis_communication.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://127.0.0.1', cast=Csv())

if not DEBUG:
    # Security settings for production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Email configuration

 
EMAIL_BACKEND=config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')  
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@libis.com')
DOMAIN = config('DOMAIN', default='localhost:8000')

# Custom User Model
AUTH_USER_MODEL = 'core.User'
# Custom settings
SITE_NAME = "Libis Communication"
SITE_DOMAIN = config('SITE_DOMAIN', default='localhost:8000')
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Custom user model
AUTH_USER_MODEL = 'core.User'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
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
        'level': 'WARNING',
    },
}