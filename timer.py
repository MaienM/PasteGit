import time

from flask import request
from werkzeug.wsgi import ClosingIterator

def start():
    """
    Start the timing of the request time.
    """
    request.start = time.time()

def end(response):
    """
    End the timing of the request time, and insert the time into the page result.
    """
    if isinstance(response.response, ClosingIterator):
        return response

    diff = time.time() - request.start
    del request.start

    if response.response:
        response.response[0] = response.response[0].replace('__EXECUTION_TIME__', '{:.3}'.format(diff))
        response.headers["content-length"] = len(response.response[0])

    return response
