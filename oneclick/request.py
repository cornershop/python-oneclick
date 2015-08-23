class Request(object):
    _params = None

    def __init__(self, **kwargs):
        self._params = kwargs

    @property
    def params(self):
        return self._params
