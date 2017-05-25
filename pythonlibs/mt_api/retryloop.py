# retry loop from http://code.activestate.com/recipes/578163-retry-loop/
import time
import sys


class RetryError(Exception):
    pass


def retryloop(attempts, timeout=None, delay=0, backoff=1):
    starttime = time.time()
    success = set()
    for i in range(attempts): 
        success.add(True)
        yield success.clear
        if success:
            return
        duration = time.time() - starttime
        if timeout is not None and duration > timeout:
            break
        if delay:
            time.sleep(delay)
            delay *= backoff

    e = sys.exc_info()[1]

    # No pending exception? Make one
    if e is None:
        try:
            raise RetryError
        except RetryError as exc:
            e = exc

    # Decorate exception with retry information:
    e.args = e.args + ("on attempt {0} of {1} after {2:.3f} seconds".format(
        i + 1, attempts, duration), )

    raise e
