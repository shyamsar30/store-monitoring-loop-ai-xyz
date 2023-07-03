import time
from celery  import shared_task

@shared_task()
def add(a, b):
    time.sleep(5)