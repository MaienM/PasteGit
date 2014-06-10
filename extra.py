import time

from flask import request

def timer_start():
    """
    Start the timing of the request time.
    """
    request.start = time.time()

def timer_end(response):
    """
    End the timing of the request time, and insert the time into the page result.
    """
    diff = time.time() - request.start
    del request.start

    if (response.response):
        response.response[0] = response.response[0].replace('__EXECUTION_TIME__', '{:.3}'.format(diff))
        response.headers["content-length"] = len(response.response[0])

    return response
