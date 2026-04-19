"""
Cấu hình Django cho dự án Quản lý Cửa hàng Con Cưng
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-concung-secret-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Ứng dụng đã cài đặt
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',          # GeoDjango

    # Ứng dụng của dự án
    'accounts',
    'stores',
    'products',
    'orders',
    'gis_utils',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'concung.middleware.PermissionsPolicyMiddleware',  # GPS + OSM tile headers
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'concung.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Cấu hình PostgreSQL + PostGIS
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'concung_db',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Xác thực mật khẩu
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.NguoiDung'

LOGIN_URL = '/accounts/dang-nhap/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/dang-nhap/'

# API Key cho Geocoding (có thể dùng Nominatim miễn phí)
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
NOMINATIM_USER_AGENT = 'concung_app'

if os.name == 'nt':  # Windows
    GDAL_LIBRARY_PATH = r'C:\Users\TRUNG\AppData\Local\Programs\OSGeo4W\bin\gdal312.dll'
    GEOS_LIBRARY_PATH = r'C:\Users\TRUNG\AppData\Local\Programs\OSGeo4W\bin\geos_c.dll'
    PROJ_LIB = r'C:\Users\TRUNG\AppData\Local\Programs\OSGeo4W\share\proj'
    os.environ['PATH'] = r'C:\Users\TRUNG\AppData\Local\Programs\OSGeo4W\bin' + ';' + os.environ.get('PATH', '')


# Permissions-Policy: cho phép Geolocation API hoạt động
# Cần thiết để navigator.geolocation.getCurrentPosition() hoạt động
# khi truy cập qua một số browser với chính sách restrictive
SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'
