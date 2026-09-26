from celery import shared_task
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def test_connection_task():
    message = "Celery is successfully connected and running!"
    logger.info(message)
    return message

@shared_task
def long_running_task(duration):
    logger.info(f"Starting long task for {duration} seconds...")
    time.sleep(duration)
    message = f"Task completed after {duration} seconds."
    logger.info(message)
    return message