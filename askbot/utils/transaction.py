"""Utilities for working with database transactions"""
from django.conf import settings as django_settings
from django.core.signals import request_finished

class DummyTransaction(object):
    """Dummy transaction class
    that can be imported instead of the django
    transaction management and debug issues
    inside the code running inside the transaction blocks
    """
    @classmethod
    def commit(cls):
        pass


#a utility instance to use instead of the normal transaction object
dummy_transaction = DummyTransaction()

def defer_celery_task(task, **task_kwargs):
    if django_settings.CELERY_ALWAYS_EAGER:
        task.apply_async(**task_kwargs)
    else:
        def schedule_task(sender, **kwargs):
            task.apply_async(**task_kwargs)
        request_finished.connect(schedule_task)
