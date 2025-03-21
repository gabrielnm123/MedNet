import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

def str_to_bool(value):
    return value.lower() == 'true'

SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')

DEBUG = str_to_bool(os.environ.get('DEBUG', 'True'))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'mednet_db'),
        'HOST': os.environ.get('MYSQL_HOST', '0.0.0.0'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
        'USER': os.environ.get('MYSQL_USER', 'root'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'root_password'),
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'recepcao_principal',
    'dal',
    'dal_select2',
    'rest_framework',
    'rest_framework_simplejwt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = "MedNet.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = "MedNet.wsgi.application"

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'en-us')

TIME_ZONE = os.environ.get('TIME_ZONE', 'America/Fortaleza')

USE_I18N = str_to_bool(os.environ.get('USE_I18N', 'True'))
USE_TZ = str_to_bool(os.environ.get('USE_TZ', 'True'))
USE_L10N = str_to_bool(os.environ.get('USE_L10N', 'False'))

DATETIME_FORMAT = os.environ.get('DATETIME_FORMAT', 'd/m/Y H:i:s')

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))
if not DEBUG:
    STATICFILES_STORAGE = os.environ.get(
        'STATICFILES_STORAGE',
        'whitenoise.storage.CompressedManifestStaticFilesStorage'
    )


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('ACCESS_TOKEN_LIFETIME', 365))),
}

SESSION_COOKIE_AGE = int(os.environ.get('SESSION_COOKIE_AGE', 1800))

DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.environ.get('DATA_UPLOAD_MAX_NUMBER_FIELDS', 0)) or None
