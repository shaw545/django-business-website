from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY
SECRET_KEY = 'django-insecure-change-this-key'
DEBUG = True
ALLOWED_HOSTS = []


# APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'website',
]


# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# URL CONFIG
ROOT_URLCONF = 'business_site.urls'


# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],   # using app templates (website/templates)
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = []


# LANGUAGE
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# 🔥 STATIC FILES (THIS FIXES YOUR IMAGE)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',   # this points to your static folder
]


# 🔥 MEDIA FILES (for uploads later)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# DEFAULT ID
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'