from .base import *

SECRET_KEY = 'django-insecure-test-secret-key-only-for-testing'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
