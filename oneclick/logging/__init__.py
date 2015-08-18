__all__ = ['logger', 'BaseHandler', 'NullHandler']


LOG_DATE_FORMAT = "%d%m%Y"
LOG_TIME_FORMAT = "%H%M%S"


class BaseHandler(object):

    def event_generic(self, **kwargs):
        raise NotImplementedError()


class NullHandler(BaseHandler):

    def event_generic(self, **kwargs):
        pass


class Logger(object):

    def __init__(self, handler):
        self.set_handler(handler)

    def set_handler(self, handler):
        self.handler = handler

    def generic(self, action, request, response):
        # request
        params = request.params
        params['action'] = action
        params['type'] = 'REQUEST'
        self.handler.event_generic(**params)
        # response, TODO: handle error
        if response.is_valid():
            params = response.params
            params['type'] = 'RESPONSE'
            params['action'] = action
            self.handler.event_generic(**params)
        else:
            params = {'error': response.error, 'error_msg': response.error_msg,
                      'user_error_msg': response.user_error_msg, 'extra': response.extra}
            params['type'] = 'RESPONSE'
            params['action'] = action
            self.handler.event_generic(**params)


logger = Logger(NullHandler())


def configure_logger(handler):
    logger.set_handler(handler)
