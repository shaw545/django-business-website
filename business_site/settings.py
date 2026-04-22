import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JS, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Login settings
LOGIN_REDIRECT_URL = '/seller/dashboard/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'

# Platform fee (THIS FIXES YOUR ERROR)
PLATFORM_FEE_PERCENT = 2

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'