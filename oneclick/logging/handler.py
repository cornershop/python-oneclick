# encoding=UTF-8
from __future__ import unicode_literals

import os
import datetime
from contextlib import closing

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

        for k, v in list(kwargs.items()):
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
