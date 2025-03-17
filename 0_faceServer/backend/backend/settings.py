import os
from pathlib import Path

# ✅ BASE_DIR 설정 (backend 폴더 기준)
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ `masked_image/` 폴더를 미디어 경로로 설정 (Django가 이 경로에서 파일을 제공함)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "detection", "masked_image")  # ✅ 올바른 저장 경로 설정

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-yi(a9p@9y513r&p4__qq--ivz$8gqub4j6m*8yh@x=&bj1%%d)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "203.255.178.158",  # 서버 IP 추가
    "*",  # 🚀 모든 외부 IP 허용 (테스트용, 운영환경에서는 비추천)
]

# ✅ INSTALLED_APPS 설정
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'detection',  # ✅ detection 앱 추가
]

# ✅ Middleware 설정
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ✅ CORS 설정 (모든 도메인 허용)
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'

# ✅ SQLite 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ✅ Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ✅ Internationalization
LANGUAGE_CODE = 'ko-kr'  # ✅ 한국어 설정
TIME_ZONE = 'Asia/Seoul'  # ✅ 한국 시간대로 변경
USE_I18N = True
USE_TZ = True

# ✅ Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# ✅ Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
