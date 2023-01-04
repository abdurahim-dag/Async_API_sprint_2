"""
Django settings for config project.
"""
import os

from pathlib import Path
from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include('components/database.py')
include('components/middleware.py')
include('components/installed_apps.py')
include('components/middleware.py')
include('components/templates.py')
include('components/auth_passwords_validators.py')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', True) == 'True'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:8080",]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOCALE_PATHS = ['movies/locale']

INTERNAL_IPS = [
    "127.0.0.1",
]

if DEBUG:
    # for swagger
    include('components/cors.py')