import time


from ...app import db
from celery import Celery
from celery import signature, chord
print(flask_app)

def create_celery(application):
    celery = Celery(
        application.import_name,                                #TODO why not just .name?
        broker='amqp://guest:guest@localhost',          #TODO not-hardcode after testing it properly
        backend='redis://localhost:6379'
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with application.app_context():
                return self.run(*args, **kwargs)

    celery.Task=ContextTask
    return celery


# celery = create_celery(flask_app)

# @celery.task(name='make_celery.tester')
# def tester(secs):
#     time.sleep(secs)
#     choiz = f'{secs}: nesto nesto'
#     return choiz
#
# @celery.task(name='make_celery.resultati')
# def rezultati(results):
#     return results
#     # chord(tester.s(x) for x in [1.1, 4, 3, 2, 2.2])(rezultati.s()).get()
#




print('yes')
print(__name__)