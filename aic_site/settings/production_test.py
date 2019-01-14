from .production import *
from .production_secret import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'aic_test_db',
        'PORT': 5432,
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'datadays.sharif@gmail.com'
EMAIL_HOST_PASSWORD = 'eybabatorochikarkonamdige'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'datadays@sharif.edu'
INFRA_IP = '144.202.6.232'
INFRA_PORT = '8000'
INFRA_URL = 'http://{}:{}'.format(INFRA_IP, INFRA_PORT)
INFRA_API_SCHEMA_ADDRESS = "{}/api/schema/".format(INFRA_URL)

SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


