from response import Response
from .logging import logger
from .transport import get_Http
import sys
if sys.version > '3':
    unicode = str


class Client(object):
    client = None
    location = None
    _testing = None
    http = None

    def __init__(self, testing=False):
        self._testing = testing
        self.location = "https://webpay3g.orangepeople.cl:443/webpayserver/wswebpay/OneClickPaymentService"
        Http = get_Http()
        self.http = Http(timeout=20)


    def send(self, action, xml):
        http_method = str('POST')
        location = str(self.location)
        soap_action = str(action)

        headers = {
            'Content-type': 'text/xml; charset="UTF-8"',
            'Content-length': str(len(xml)),
            'SOAPAction': '"%s"' % soap_action
        }

        if sys.version < '3':
            headers = dict((str(k), str(v)) for k, v in headers.items())

        response, content = self.http.request(
            location, http_method, body=xml, headers=headers)

        return content

    def request(self, action, xml):
        response_content = self.send(action, xml)
        response = Response(response_content, action, self._testing)
        return response
