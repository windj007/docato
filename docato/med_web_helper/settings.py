# -*- coding: utf8 -*-
# Django settings for med_web_helper project.

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'med_web_helper',
        'USER' : 'root',
        'PASSWORD' : 'pwd',
        'HOST' : 'med-web-helper-mysql', # MYSQL_HOST
        'PORT' : 3306,
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
             ('ru', u'Русский'),
             ('en', 'English'),
             )

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

MEDIA_URL = '/docato/data/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/docato/src/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4&r89czckb8fqmjon_*3y(@w%7e)8%^_t&s8@(i862#g_aeu#5'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'med_web_helper.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'med_web_helper.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
#    'djcelery',
    'navigator',
    'django_tables2',
    'bootstrap3',
    'guardian',
    'polymorphic'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
	'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'common': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename' : '/docato_data/log/common.log',
            'formatter' : 'verbose'
        },
        'preprocessing': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename' : '/docato_data/log/preprocessing.log',
            'formatter' : 'verbose'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'common': {
            'handlers': ['common'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'preprocessing': {
            'handlers': ['preprocessing'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

LOGIN_URL = "django.contrib.auth.views.login"

TEMPLATE_CONTEXT_PROCESSORS = [
                               "django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.request"
                               ]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
)

DEFAULT_FILE_STORAGE = 'navigator.filestorage.SlugifiedFileSystemStorage'

ANONYMOUS_USER_ID = -1

CONVERTED_PAGE_WIDTH = 1000
COLORS_NUMBER = 200

TIKA_PREFIX = '/docato/thirdparty/tika/'
