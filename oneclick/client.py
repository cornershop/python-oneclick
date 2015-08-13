from pysimplesoap.client import SoapClient
from response import Response


class Client(object):
    client = None
    _testing = None

    def __init__(self, testing=False):
        self._testing = testing
        self.client = SoapClient(
            soap_ns='soap11',
            location="https://webpay3g.orangepeople.cl:443/webpayserver/wswebpay/OneClickPaymentService",
            namespace="http://webservices.webpayserver.transbank.com/",
            trace=True)

    def request(self, action, xml):
        response_content = self.client.send('initInscription', xml)
        print "############"
        print response_content
        response = Response(response_content, action, self._testing)
        return response
