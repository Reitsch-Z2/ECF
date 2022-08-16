import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_temp_key'  # TODO server setup later on
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')  # TODO server setup later on

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 65
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'markorajic.arch@gmail.com'
    ADMINS =['markorajic.arch@gmail.com']

    CELERY_BROKER_URL = 'amqp://guest:guest@localhost'                  # TODO temp local
    RESULT_BACKEND = 'redis://localhost:6379/0'             # TODO temp local
