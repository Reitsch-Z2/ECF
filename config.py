import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_temp_key'  # TODO server setup later on
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 65
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'ecf.assistance@gmail.com'
    ADMINS =['ecf.assistance@gmail.com']

    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    RESULT_BACKEND = os.environ.get('RESULT_BACKEND')
