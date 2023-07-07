"""
Django settings for ecomm_app project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import environ

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENVIROMENT = os.environ.get('ENV')
if ENVIROMENT == 'kees':
    environ.Env.read_env(env_file=os.path.join(BASE_DIR, 'settings/enviroments/.env.kees'))
elif ENVIROMENT == 'pcb':
    environ.Env.read_env(env_file=os.path.join(BASE_DIR, 'settings/enviroments/.env.pcb'))
elif ENVIROMENT == 'comverse':
    environ.Env.read_env(env_file=os.path.join(BASE_DIR, 'settings/enviroments/.env.comverse'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "l^c7%hr7*ikley*)9bja_jj*o0$19pcm5zgpmcx0&ri2p@s+hf"

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True
ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Dependant Libraries
    'rest_framework',                   # Django Rest Framework Libraries for Internal API
    'corsheaders',                      # Django Cross Origin Resource Sharing Library
    'drf_yasg',                         # Django API Swagger documentation linked with DRF
    'rest_framework.authtoken',         # Django Rest Framework Token Authentication
    # 'django_apscheduler',               # Schedule Tasks

    # Custom Apps
    'cms',                              # (Content Management System)
    'authentication',                   # (User Authentication Module)
    'setting',                          # (Store Settings and Information)
    'crm',                              # (Customer Relationship Management)
    'products',                         # (Master Data Products Management)
    'vendor',                           # (Vendor Management Module)
    'storefront',                       # (StoreFront API Management Module)
    'discount',                         # (Discount API Management Module)
    'order',                            # (Orders API Management Module)
    'dashboard',                        # (Dashboard Management Module)
    'paymentgateway',                   # (Payment Gateway Module)
    'shipping',                         # (Shipping Module)
    'notification',                     # (Notifications Module)
    'social_feed',                      # (social feed Module)
]

AUTH_USER_MODEL = 'authentication.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # make all endpoints private
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'authentication.custom_authentication.TokenAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle'
        ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'user': '100/minute'
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'ecomm_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ecomm_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases


# Kees Cloud Live Credentials
DATABASES = {
    'default': {
        'ENGINE': env('ENGINE'),
        'NAME': env('NAME'),
        'CONN_MAX_AGE': 3600,
        'USER': env('USERNAME'),
        'PASSWORD': env('LIVE_PASSWORD'),
        'HOST': env('LIVE_HOST'),
        'PORT': env('PORT'),
    },
    'OPTIONS': {
        'timeout': 20,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'Asia/Karachi'
TIME_ZONE = 'Asia/Qatar'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/Static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "Static"), "templates"]

STATIC_ROOT = "/Static/"

SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
   }
}

# Live Credentials
HOST_URL = env("HOST_URL")
VENDOR_URL = env("VENDOR_URL")
CLIENT_URL = env("CLIENT_URL")
STOREFRONT_URL = env("STOREFRONT_URL")
IMAGEKIT_URL = "https://ik.imagekit.io/z9qkagamlmm/kees"

# Kees email setup
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# templates absolute path
ACCEPT_INVITE = os.path.abspath("authentication/templates/email_invite.html")
FORGOT_PASSWORD = os.path.abspath("authentication/templates/user_forgot_password.html")
CONFIRM_ORDER = os.path.abspath("authentication/templates/order.html")
ORDER_INVOICE = os.path.abspath("authentication/templates/invoice.html")
PAY2M_TEMPLATE = os.path.abspath("paymentgateway/templates/pay2m.html")

# Kees AWS
AWS_BASE_URL = env('AWS_BASE_URL')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_PATH = env('AWS_BUCKET_PATH')

AWS_ELASTIC_DOMAIN = env('AWS_ELASTIC_DOMAIN')
AWS_ELASTIC_USERNAME = env('AWS_ELASTIC_USERNAME')
AWS_ELASTIC_PASSWORD = env('AWS_ELASTIC_PASSWORD')
AWS_ELASTIC_SEARCH_INDEX_NAME = env('LIVE_AWS_ELASTIC_SEARCH_INDEX')

LOYALTY_MICROSERVICE_URL = env('LOYALTY_MICROSERVICE_URL')
