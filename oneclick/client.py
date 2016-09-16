from socket import error as SocketError
import errno

from pysimplesoap.client import SoapClient
from response import Response


class Client(object):
    client = None
    _testing = None

    def __init__(self, testing=False):
        self._testing = testing
        if testing:
            location = 'https://webpay3gint.transbank.cl/webpayserver/wswebpay/OneClickPaymentService'
        else:
            location = 'https://webpay3g.transbank.cl:443/webpayserver/wswebpay/OneClickPaymentService'

        self.client = SoapClient(
            soap_ns='soap11',
            location=location,
            namespace="http://webservices.webpayserver.transbank.com/",
            timeout=20,
            trace=True
        )

    def request(self, action, xml):
        try:
            return Response(self.client.send(action, xml), action, True)
        except SocketError as e:
            if e.errno == errno.ECONNRESET:
                response_error = Response("ECONNRESET", action)
                response_error.error, response_error.error_msg = "ECONNRESET", "[Errno 104] Connection reset by peer"
                return response_error
            else:
                raise
