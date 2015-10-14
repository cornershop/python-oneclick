# encoding=UTF-8
from __future__ import unicode_literals

import os
import datetime
from contextlib import closing
import logging
import logging.config

from loggly.handlers import HTTPSHandler
import pytz


LOGGLY_LOG_NAME = "OneClick"
EVENTS_LOG_FILE_NAME_FORMAT = "TBK_EVN%s.log"
EVENTS_LOG_FILE_DATE_FORMAT = "%Y%m%d"


class SimpleHandler(object):
    def __init__(self, path=None):
        self.path = path

    def event_generic(self, **kwargs):
        event_type = kwargs.pop('type')
        event_info = '{} ({}) \n'.format(event_type, kwargs['action'])

        for k, v in kwargs.items():
            event_info = '{}\t{} => {}\n'.format(event_info, k, v)

        with closing(self.events_log_file) as events_log_file:
            events_log_file.write(event_info)

    @property
    def events_log_file(self):
        return self.log_file(EVENTS_LOG_FILE_NAME_FORMAT, EVENTS_LOG_FILE_DATE_FORMAT)

    def log_file(self, log_file_name_format, log_file_date_format):
        santiago = pytz.timezone('America/Santiago')
        now = santiago.localize(datetime.datetime.now())
        file_name = log_file_name_format % now.strftime(log_file_date_format)
        return open(os.path.join(self.path, file_name), 'a+')


class LogglyHandler(object):
    def __init__(self, api_key=None):
        self.api_key = api_key

    def event_generic(self, **kwargs):
        event_type = kwargs.pop('type')
        #  set basic keys
        extra = {'event_type': event_type, 'action': kwargs['action']}
        #  set keys
        for k, v in kwargs.items():
            if k in ['token', 'tbkUser']:  # hide private info
                extra[k] = v[-4:]
            else:
                extra[k] = v
        #  format message
        message = '{} => {}'.format(event_type, kwargs['action'])

        self.log_event(message=message, extra=extra)

    def format_msg(self, extra):
        base_fmt = '{"loggerName":"%(name)s", "asciTime":"%(asctime)s", "fileName":"%(filename)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"'
        fmt_extra = u''
        for k, v in extra.items():
            key = str(k).decode('unicode_escape').encode('ascii','ignore')
            value = str(v).decode('unicode_escape').encode('ascii','ignore')
            fmt_extra = '{}, "{}": "{}"'.format(fmt_extra.encode('ascii','ignore'), key, value)

        return base_fmt + fmt_extra + '}'

    def log_event(self, message, extra):
        logger = logging.getLogger(LOGGLY_LOG_NAME)
        syslog = HTTPSHandler('https://logs-01.loggly.com/inputs/{}/tag/python'.format(self.api_key), 'POST')
        formatter = logging.Formatter(self.format_msg(extra))
        syslog.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(syslog)
        logger = logging.LoggerAdapter(logger, {})
        logger.info(message)