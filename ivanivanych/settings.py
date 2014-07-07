# -*- coding: utf-8 -*-
"""
Django settings for ivanivanych project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k3363a(v)8azt%(typu%5v#%e3c=%#*uo9s^oo9r4w*oi83-gv'

IP_SALT = '1234567'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'south',
    'social.apps.django_app.default',
    'astromap',
)

MIDDLEWARE_CLASSES = (
    'django_dont_vary_on.middleware.RemoveUnneededVaryHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.open_id.OpenIdAuth',
    'social.backends.google.GoogleOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.vk.VKOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

ROOT_URLCONF = 'ivanivanych.urls'

WSGI_APPLICATION = 'ivanivanych.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'nska',
        'USER': 'nska',
        'PASSWORD': 'testpass',
    }
}


# Caches

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('ru', u'Русский'),
    ('en', u'English'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'astromap', 'templates'),
)

GOOGLE_MAPS_KEY = 'AIzaSyBC72uiKsPtdVqm-ncDshonzmUABv-Ra-A'

FEED_SIZE = 20


# Social auth

LOGIN_REDIRECT_URL = '/astromap/'
#
SOCIAL_AUTH_VK_OAUTH2_KEY = '3811391'
SOCIAL_AUTH_VK_OAUTH2_SECRET ='5Ny1IqHY9u4cG5OywafO'
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email']

# Test app credentials
SOCIAL_AUTH_FACEBOOK_KEY = '882015901813524'
SOCIAL_AUTH_FACEBOOK_SECRET = 'fdf1d22c074c6bd9dc895fc7ff452191'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
