from celery import Celery


def create_celery(application):
    """
    A function used to create an instance of a Celery application - it configures the messaging broker and the
    results backend for the Celery, and adds Flask's application context to the Celery tasks.
    """
    celery = Celery(
        application.import_name,
        broker=application.config['CELERY_BROKER_URL'],
        result_backend=application.config['RESULT_BACKEND']
    )
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with application.app_context():
                return self.run(*args, **kwargs)

    celery.Task=ContextTask
    return celery
