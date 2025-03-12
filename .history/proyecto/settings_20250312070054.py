"""
Django settings for proyecto project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import environ


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+xob$tnz-6$38v)e@z8t6nt&6+)7)q4@_sd)l*51yeyxg*2r3b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['casakolo1.pythonanywhere.com', 'localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    # 'admin_interface',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'casaKolor1',
    'django.contrib.humanize',
]
JAZZMIN_SETTINGS = {
    # Cambiar título y encabezado
    "site_title": "Casa Kolor Admin",  
    "site_header": "Casa Kolor",
    "welcome_sign": "Bienvenido al Panel de Administración de Casa Kolor",
    "copyright": "© 2025 Casa Kolor",  

    # Agregar logo personalizado (debe estar en /static/images/)
    "site_logo": "images/casakolor1.png",  # Asegúrate de que el logo esté en /static/images/
    "site_logo_classes": "img-circle",  # Opcional: Puedes cambiar la forma del logo

    # Cambiar favicon
    "site_icon": "images/favicon.ico",  # Asegúrate de tener un favicon en /static/images/

    # Colores personalizados
    "primary_color": "#ff6600",  # Cambia este color por el de tu marca
    "secondary_color": "#0055a5",
    "dark_mode_toggle": True,  # Habilita modo oscuro

    # Orden de las aplicaciones en el menú
    "order_with_respect_to": ["auth", "casaKolor1"],  

    # Personalizar iconos en el menú
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "casaKolor1.Producto": "fas fa-paint-brush",  # Cambia según el modelo
    },

    # Expandir menú por defecto
    "navigation_expanded": True,
}
JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",  # O prueba con "cyborg" si quieres más oscuro
    "navbar": "navbar-dark bg-dark",  # Cambia la barra superior a color oscuro
    "body_small_text": True,  
    "brand_colour": "white",  # Color del texto en la barra superior
}





MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proyecto.urls'
#import os
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'proyecto.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'casaKolor1','static')
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')





# Configuración de correo en settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Servidor SMTP (Gmail como ejemplo)
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'hector3208609853@gmail.com'  # Tu correo
EMAIL_HOST_PASSWORD = 'chpo lvdo nzkf xdqx'  # Contraseña o App Password si usas Gmail

# Configuración de cookies
CSRF_COOKIE_SECURE = False  # Cambiar a True solo si usas HTTPS
CSRF_COOKIE_HTTPONLY = False  # Permitir acceso vía JavaScript
SESSION_COOKIE_SECURE = False  # Cambiar a True solo si usas HTTPS

# Configuración para depuración (solo en desarrollo)
DEBUG = True  # Asegúrate que DEBUG esté en True durante desarrollo

# settings.py
LOGIN_URL = '/login/'