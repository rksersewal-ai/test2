from .base import *

# In-memory database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'SERIALIZE': False,
        },
    }
}

# Fast password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable Celery tasks during tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Avoid serializing app tables into the reusable SQLite test database.
TEST_NON_SERIALIZED_APPS = INSTALLED_APPS

# API tests should exercise auth and permissions, not LAN gating.
DISABLE_LAN_RESTRICTION = True

# WhiteNoise warns if the static root does not exist when request tests run.
STATIC_ROOT = BASE_DIR / 'staticfiles-test'
STATIC_ROOT.mkdir(exist_ok=True)
