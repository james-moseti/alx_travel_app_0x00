from __future__ import absolute_import, unicode_literals

from celery import shared_task

@shared_task
def example_task():
    print("This is an example task running in the background.")
    return "Task completed successfully."