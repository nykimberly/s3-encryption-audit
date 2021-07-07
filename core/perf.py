import logging
import functools
import time


from expiringdict import ExpiringDict
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


def timer(func):
    """Prints runtime of decorated function."""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start = time.perf_counter()
        value = func(*args, **kwargs)
        end = time.perf_counter()
        run = end - start
        logger.debug(
            f"Finished {func.__name__!r} in {run:.4f} seconds; args={args}, kwargs={kwargs}"
        )
        return value

    return wrapper_timer


def cache(max_len=128, max_age_seconds=60):
    """Basic lru cache with expiry."""

    def decorator(func):
        storage = ExpiringDict(max_len=max_len, max_age_seconds=max_age_seconds)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (*args,) + tuple([(k, v) for k, v in kwargs.items()])
            if key in storage:
                value = storage[key]
                logger.debug(f"Found cached result {value}")
            else:
                value = func(*args, **kwargs)
                logger.debug(f"No cached result, writing through: {key}: {value}")
                storage[key] = value
            return value

        return wrapper

    return decorator
