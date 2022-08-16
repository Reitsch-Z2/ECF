import time
from flask import Flask
from celery import Celery
from celery import signature, chord

print(__name__)
print('yes')
application = Flask(__name__)

application.config['CELERY_BROKER_URL'] = 'amqp://guest:guest@localhost'
# application.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
application.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

celery = Celery(
    application.name,
    broker=application.config['CELERY_BROKER_URL'],
    backend=application.config['CELERY_RESULT_BACKEND']
)
# celery.conf.update(application.config)

@celery.task(name='make_celery.tester')
def tester(secs):
    time.sleep(secs)
    # choiz = list(choice('ABCDEFG') for i in range(10))
    choiz = f'{secs}: nesto nesto'
    return choiz

@celery.task(name='make_celery.resultati')
def rezultati(results):
    return results
    # chord(tester.s(x) for x in [1.1, 4, 3, 2, 2.2])(rezultati.s()).get()

