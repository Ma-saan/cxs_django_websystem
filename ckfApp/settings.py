from pathlib import Path
import os
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@2!%qa4w+a7=c3u57(blfs-rq3h7et0lomb*z%!i@3vwi63d%%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'meetingRoom.apps.MeetingroomConfig',
    'home.apps.HomeConfig',
    'jp1.apps.Jp1Config',
    'jp2.apps.Jp2Config',
    'jp3.apps.Jp3Config',
    'jp4.apps.Jp4Config',
    'jp6a.apps.Jp6AConfig',
    'jp6b.apps.Jp6BConfig',
    'jp7.apps.Jp7Config',
    'schedule.apps.ScheduleConfig',
    'sslserver',
    'schedule_app',
    'inventory',
    'schedule_manager',
    'rest_framework',
    'corsheaders',
    'channels',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ckfApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                os.path.join(BASE_DIR, 'templates'),
                os.path.join(BASE_DIR, 'schedule_app/templates'),
                ],
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

WSGI_APPLICATION = 'ckfApp.wsgi.application'

# Channels設定
ASGI_APPLICATION = 'ckfApp.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# RESTフレームワーク設定
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # 初期段階ではすべてのアクセスを許可
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default':{ 
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'juten2',
        'USER': 'root',
        'PASSWORD': '20250205',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'meetingroom': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'meetingroom',
        'USER': 'EG001',
        'PASSWORD': 'Japan001',
        'HOST': '192.168.11.103',
        'PORT': '3306',
    },
    'juten': { #元default
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'juten2',
        'USER': 'root',
        'PASSWORD': '20250205',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'production_schedule': { #元database2
        'ENGINE': 'django.db.backends.mysql',
        'NAME':'production_schedule2',
        'USER': 'root',
        'PASSWORD': '20250205',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'schedule_app': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':'juten2',
        'USER': 'root',
        'PASSWORD': '20250205',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# React開発サーバーからのアクセスを許可する設定
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]



# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'schedule_manager/static/build'),
)

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
