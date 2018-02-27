from functools import wraps
import logging
from django.db.utils import OperationalError
import time


logging.getLogger(__name__)

def retry_on_lock(timeout=None, retries=1):
    if not timeout:
        timeout = 5
    def outer_decorator(func):
        @wraps(func)
        def inner_decorator(*args, **kwargs):
            nonlocal retries
            while retries >= 1:
                try:
                    func(*args, **kwargs)
                    break
                except OperationalError as e:
                    logging.error('{0}. Waiting for {1} seconds. Retries left: {2}'.format(repr(e), timeout, retries))
                    time.sleep(timeout)
                    retries -= 1
                except Exception as e:
                    logging.error(repr(e))
                    quit()

            if retries <= 0:
                logging.error("Can't connect to db")
                quit()

        return inner_decorator
    return outer_decorator