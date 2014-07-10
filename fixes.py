"""
Hacks for broken stuff we have to interact with.
"""

import urlparse

class MicroMock(object):
    """
    A very simple mock class.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def fb_access_token_response(r):
    """
    A fix for facebook. 

    For some reason facebook doesn't return JSON for the access_token page,
    even though the spec says they should. A spec which they co-author. Right.
    """
    values = urlparse.parse_qs(r.text)
    values = dict([(k, v[0]) for k, v in values.items()])
    values['token_type'] = 'bearer'
    fr = MicroMock(text=json.dumps(values))
    return fr
