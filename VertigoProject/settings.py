"""
Main settings file.
"""

import os

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

DEFAULT_DOMAIN = 'https://epicvertigo.xyz'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
WARFRAME_KEY = os.getenv('WARFRAME_KEY')
POESESSID = os.getenv('POESESSID')

# Discord bot settings
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_TEST_TOKEN = os.getenv('DISCORD_TEST_TOKEN')
IMGUR_ID = os.getenv('IMGUR_ID')
IMGUR_ALBUM = os.getenv('IMGUR_ALBUM')
IMGUR_SECRET = os.getenv('IMGUR_SECRET')
STEAM_API_KEY = os.getenv('STEAM_API_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv('DJANGO_DEBUG', None))

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()]
    )

LOGIN_REDIRECT_URL = 'main:home'
INTERNAL_IPS = ('127.0.0.1', 'localhost',)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') or INTERNAL_IPS
# Application definition

INSTALLED_APPS = [
    # Add your apps here to enable them
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'webgames',
    'main.apps.MainConfig',
    'discordbot.apps.DiscordbotConfig',
    'poeladder.apps.PoeladderConfig',
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'dbbackup',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',) ,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}

ROOT_URLCONF = 'VertigoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'main/templates'),
            os.path.join(BASE_DIR, 'poeladder/static'),
            os.path.join(BASE_DIR, 'discordbot', 'templates'),
            os.path.join(BASE_DIR, 'webgames', 'static'),
            os.path.join(BASE_DIR, 'webgames', 'dots'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'poeladder.context_processors.poe_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'VertigoProject.wsgi.application'

# DB backup settings

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/var/backups'}

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data.db'),  # 'db.sqlite3'
        'TEST_NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'webgames', 'dots', 'static'),
    os.path.join(BASE_DIR, 'webgames', 'dots')
]
# For production - Enable STATIC_ROOT, remove STATIC_ROOT from STATIFILES_DIRS
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# For debug - Disable STATIC_ROOT, enable STATICFILES_DIRS
# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
