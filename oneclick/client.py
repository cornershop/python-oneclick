from response import Response
import requests
from requests_toolbelt import SSLAdapter
import sys
import os
if sys.version > '3':
    unicode = str


class Client(object):
    client = None
    location = None
    _testing = None
    http = None

    def __init__(self, testing=False):
        self._testing = testing
        if testing:
            self.location = 'https://tbk.orangepeople.cl/webpayserver/wswebpay/OneClickPaymentService'
        else:
            self.location = 'https://webpay3g.transbank.cl:443/webpayserver/wswebpay/OneClickPaymentService'

    def send(self, action, xml):
        soap_action = str(action)

        headers = {
            'Content-type': 'text/xml; charset="UTF-8"',
            'Content-length': str(len(xml)),
            'SOAPAction': '"%s"' % soap_action
        }

        if sys.version < '3':
            headers = dict((str(k), str(v)) for k, v in headers.items())

        d = requests.post(self.location, data=xml, headers=headers)
        return d.text

    def request(self, action, xml):
        response_content = self.send(action, xml)
        response = Response(response_content, action, self._testing)
        return response
