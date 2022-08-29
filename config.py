import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_temp_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    if 'postgres' in SQLALCHEMY_DATABASE_URI:                       #TODOs
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres', 'postgresql')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 65
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'ecf.assistance@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS =['ecf.assistance@gmail.com']

    CELERY_BROKER_URL = os.environ.get('CLOUDAMQP_URL') or 'amqp://guest:guest@localhost'   #alt values for docker
    RESULT_BACKEND = os.environ.get('REDIS_URL') or "redis://localhost:6379/0"              # images - for testing
