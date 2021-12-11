from .base import *
import dj_database_url
import environ

env = environ.Env()
env.read_env('.env')

SECRET_KEY = env('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ['https://ai-coach-eiji-handstand-v3.herokuapp.com/']

DATABASES = { 
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "env('DATABASE_NAME')",
        'USER': "env('DATABASE_USER_NAME')",
        'PASSWORD': "env('DATABASE_PASSWORD')",
        'HOST': "https://ai-coach-eiji-handstand-v3.herokuapp.com/",
        'PORT': '5432',
    }
}

db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
DATABASES['default'].update(db_from_env)