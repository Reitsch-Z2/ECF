import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_temp_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    if 'postgres' in SQLALCHEMY_DATABASE_URI:                       # TODO
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres', 'postgresql')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'assistance.ecf@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS =['assistance.ecf@gmail.com']

    CELERY_BROKER_URL = os.environ.get('CLOUDAMQP_URL') or 'amqp://guest:guest@rabbit:5672'     # Alt values for docker
    RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://redis:6379/0'                      # compose
