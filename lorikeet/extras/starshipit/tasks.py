from celery import shared_task
from .submit import submit_orders as do_submit_orders


@shared_task
def submit_orders():
    do_submit_orders()
