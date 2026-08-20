from pathlib import Path
from django.conf.locale.fr import formats
import os 
from dotenv import load_dotenv


formats.NUMBER_GROUPING = 3


load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # ----- LES NOUVEAUX PAQUETS (API) -----
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders', 
    'django_filters',
    
     # ----- NOS APPS (créées par nous) -----
    
    'auth_app',         # Gère les utilisateurs (connexion, inscription)
    'client_app',       # Portail client
    'order_app',        # Panier et commandes
    'paiement_app',     # Paiements
    'products_app',     # Pièces détachées
    'vehicul_app',      # Catalogue voitures
    'directeur_app',    # Dashboard directeur
    'commercial_app',   # Dashboard commercial
    'chat_app',         # Messagerie client-commercial
    'dashboard_app',     # Dashboard global
    'leads_app',        # Demandes de crédit
    'maintenance_app',    # Suivi des maintenances
        # les App site-web
    'home_app',
    'services_app',
    
    #tailwind_app
    "tailwind",
    "theme",
]

# ----- MIDDLEWARE (filtres qui s'exécutent à chaque requête) -----
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',# 👈 Doit être le PLUS HAUT
    # Pourquoi ? Parce qu'il doit traiter la requête AVANT les autres
    # Il ajoute les en-têtes CORS (Access-Control-Allow-Origin, etc.)
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # ✅ AJOUTE CETTE LIGNE (en bas de la liste)
    'koz_flow.middleware.LastActivityMiddleware',
]

# ----- CONFIGURATION DE DRF (Django Rest Framework) -----
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS' : [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


# ----- CONFIGURATION DES TOKENS JWT -----
from datetime import timedelta

SIMPLE_JWT = {
    #ACCES_TOKEN_LIFETIME
    # Après 60 minutes, le token expire et tu dois en demander un nouveau
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    
    #REFRESH_TOKEN_LIFETIME
    # Pendant 7 jours, tu peux utiliser le refresh token pour obtenir un nouveau access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    
    #ROTATE_REFRESH_TOKENS
    #change les tokens à chaque refresh , plus de secur
    
    'ROTATE_REFRESH_TOKENS':True,
    
    #BLACKLIST_AFTER_ROTATION = True
    #les ancien tokens sont blacklisté plus reutilisable
    'BLACKLIST_AFTER_ROTATION': True,    
    
}

# ----- CONFIGURATION CORS (qui a le droit d'appeler nos APIs) -----
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",      # Ton site web en développement
    "http://127.0.0.1:8000", # Pareil mais avec IP
    'http://187.127.233.39',
    'https://koz-corporate.pro',
    'https://www.koz-corporate.pro',
    #"https://kozservices.bf",     # Ton site web en production (quand il sera en ligne)
]

# CORS_ALLOW_CREDENTIALS = True
# Permet d'envoyer les cookies et les en-têtes d'authentification
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'koz_flow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR/"templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'koz_flow.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR /"db" /'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'defaut':{
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }
    




# URL de redirection APRÈS login réussi
LOGIN_REDIRECT_URL = '/'  # Ou '/dashboard/', '/home/', etc.

# URL de la palocalge de login
LOGIN_URL = '/'  # ✅ Correct si tu as une vue à /login/

# Optionnel: URL de logout
LOGOUT_REDIRECT_URL = '/'  # Où rediriger après logout


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'  # ou ton fuseau
USE_I18N = True
USE_L10N = True
USE_TZ = True  # TRÈS IMPORTANT !

# Format d'affichage par défaut
DATETIME_FORMAT = 'd/m/Y H:i:s'
DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i:s'


#AUTHENTICATION
AUTH_USER_MODEL = "auth_app.kozUser"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = "media/"
STATIC_ROOT = os.path.join(BASE_DIR / "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR / "media/")
STATICFILES_DIRS = [os.path.join(BASE_DIR / "koz_flow/static/"),
                    os.path.join(BASE_DIR / "static/")
                    ]

# Taille max d'upload (augmenter pour les vidéos)
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB

# Types MIME autorisés pour les vidéos
VIDEO_MIME_TYPES = [
    'video/mp4',
    'video/webm',
    'video/ogg',
    'video/quicktime',
    'video/x-msvideo',
]

#Tailwind configurations
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = [
    "127.0.0.1"
                ]

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"

#Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465  # Port SSL
EMAIL_USE_SSL = True  # Au lieu de TLS
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

#LIGDICASH configurations
LIGDICASH_API_KEY = os.getenv("LIGDICASH_API_KEY")
LIGDICASH_API_TOKEN = os.getenv("LIGDICASH_API_TOKEN")


# Sécurité CSRF pour HTTPS
# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    'http://187.127.233.39',
    'http://localhost',
    'http://127.0.0.1',
    'https://koz-corporate.pro',
    'https://www.koz-corporate.pro',
    
]

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'