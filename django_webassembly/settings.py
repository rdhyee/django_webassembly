"""
Django settings for django_webassembly project.

This is a WebAssembly-based Django application that runs entirely in the browser.
Some settings (like SECRET_KEY) are intentionally hardcoded because:
1. There is no server - the app runs client-side only
2. Each user has their own isolated instance
3. The database is local to each browser

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY NOTE: This SECRET_KEY is intentionally hardcoded for browser-only operation.
# In a traditional Django deployment, this would be a security risk, but since this
# application runs entirely client-side with no server, each user effectively has
# their own isolated instance. The key is used for session cookies and CSRF tokens
# which only exist in the user's own browser.
SECRET_KEY = "django-webassembly-browser-only-key-not-for-server-use"

# Debug mode - can be toggled for development
# In browser-only mode, debug info is visible only to the local user
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

# Hosts that are allowed to serve this application
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "testserver",
    # Add your deployment domain here
    "django-webassembly.mattbutterfield.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://django-webassembly.mattbutterfield.com",
]


# Application definition

INSTALLED_APPS = [
    "django_webassembly.apps.DjangoWebassemblyConfig",
    "django_webassembly.polls.apps.PollsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_webassembly.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_webassembly.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Using SQLite which runs in-memory in the browser via Pyodide

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
