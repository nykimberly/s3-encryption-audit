import logging
import functools
import time


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


def cache(size_limit=0, ttl=0):
    """lru_cache but with expiry"""

    def decorator(func):
        storage = {}
        ttls = {}

        def wrapper(*args, **kwargs):
            key = (*args,) + tuple([(k, v) for k, v in kwargs.items()])
            if key in storage:
                result = storage[key]
                logger.debug(f"Found cached result {result}")
            else:
                result = func(*args, **kwargs)
                storage[key] = result
                if ttl != 0:
                    ttls[key] = time.time() + ttl
                if size_limit != 0 and len(storage) > size_limit:
                    oldest_key = list(storage.keys())[0]
                    del storage[oldest_key]
            if ttl != 0:
                while len(storage.keys()):
                    oldest_key = list(storage.keys())[0]
                    if ttls[oldest_key] < time.time():
                        del storage[oldest_key]
                        logger.debug(f"Clearing old key: {oldest_key}")
                    else:
                        break
            return result

        return wrapper

    return decorator
