from pysimplesoap.client import SoapClient
from response import Response
from .logging import logger


class Client(object):
    client = None
    _testing = None

    def __init__(self, testing=False):
        self._testing = testing
        if testing:
            location = 'https://webpay3g.orangepeople.cl:443/webpayserver/wswebpay/OneClickPaymentService'
        else:
            location = 'https://webpay3g.transbank.cl:443/webpayserver/wswebpay/OneClickPaymentService'

        self.client = SoapClient(
            soap_ns='soap11',
            location=location,
            namespace="http://webservices.webpayserver.transbank.com/",
            timeout=20,
            trace=True)

    def request(self, action, xml):
        response_content = self.client.send(action, xml)
        response = Response(response_content, action, True)
        return response


