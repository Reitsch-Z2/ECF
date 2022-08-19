from celery import Celery

def create_celery(application):
    celery = Celery(
        application.import_name,                                #TODO why not just .name?
        broker=application.config['CELERY_BROKER_URL'],          #TODO not-hardcode after testing it properly
        result_backend=application.config['RESULT_BACKEND']
    )
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with application.app_context():
                return self.run(*args, **kwargs)
    celery.Task=ContextTask
    return celery
