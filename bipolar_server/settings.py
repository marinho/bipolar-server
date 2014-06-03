"""
Django settings for project bipolar_server.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(__file__)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*37-vain_#8)-ezx-9ld$yky&sdgfetmm3x8odi^+hbpkg*sg('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "tastypie",
    "social.apps.django_app.default",
    "bipolar_server.toggle",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'bipolar_server.urls'

WSGI_APPLICATION = 'bipolar_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
        os.path.join(PROJECT_DIR, "public", "static"),
        )

from bipolar_server import version
BIPOLAR_VERSION = version.version_number

TASTYPIE_DEFAULT_FORMATS = ['json']
API_LIMIT_PER_PAGE = 10

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.core.context_processors.tz',
        'django.contrib.messages.context_processors.messages',
        'social.apps.django_app.context_processors.backends',
        "bipolar_server.context_processors.toggle",
        )

AUTHENTICATION_BACKENDS = (
        'social.backends.github.GithubOAuth2',
        'django.contrib.auth.backends.ModelBackend',
        #'social.backends.email.EmailAuth',
        #'social.backends.username.UsernameAuth',
        #'social.backends.google.GoogleOAuth',
        #'social.backends.google.GoogleOAuth2',
        #'social.backends.google.GoogleOpenId',
        #'social.backends.google.GooglePlusAuth',
        )

#AUTH_USER_MODEL = 'bipolar_server.toggle.SocialUser'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'
URL_PATH = ''
SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'
#SOCIAL_AUTH_GOOGLE_OAUTH_SCOPE = [
#    'https://www.googleapis.com/auth/drive',
#    'https://www.googleapis.com/auth/userinfo.profile'
#]
## SOCIAL_AUTH_EMAIL_FORM_URL = '/signup-email'
#SOCIAL_AUTH_EMAIL_FORM_HTML = 'email_signup.html'
#SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'example.app.mail.send_validation'
#SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/email-sent/'
## SOCIAL_AUTH_USERNAME_FORM_URL = '/signup-username'
#SOCIAL_AUTH_USERNAME_FORM_HTML = 'username_signup.html'
#
#SOCIAL_AUTH_PIPELINE = (
#    'social.pipeline.social_auth.social_details',
#    'social.pipeline.social_auth.social_uid',
#    'social.pipeline.social_auth.auth_allowed',
#    'social.pipeline.social_auth.social_user',
#    'social.pipeline.user.get_username',
#    'example.app.pipeline.require_email',
#    'social.pipeline.mail.mail_validation',
#    'social.pipeline.user.create_user',
#    'social.pipeline.social_auth.associate_user',
#    'social.pipeline.social_auth.load_extra_data',
#    'social.pipeline.user.user_details'
#)

# THESE MUST BE IN local_settings.py
SOCIAL_AUTH_GITHUB_KEY = ''
SOCIAL_AUTH_GITHUB_SECRET = ''

try:
    from local_settings import *
except ImportError:
    pass
