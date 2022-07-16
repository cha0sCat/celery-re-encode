import sys

from celery import Celery
from config import BROKER, BACKEND


app = Celery(
    'celery-re-encode',
    broker=BROKER,
    backend=BACKEND,
    include=['tasks']
)

app.conf.update(
    # task_ignore_result=True,
    # task_store_errors_even_if_ignored=True,
    task_soft_time_limit=2*60*60,  # 2 hours
    task_track_started=True,
)

from celery.app.task import Task
Task.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)


if __name__ == '__main__':
    app.start(sys.argv[1:] or ['worker', '--loglevel', 'INFO'])
