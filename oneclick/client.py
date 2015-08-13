from pysimplesoap.client import SoapClient
from response import Response


class Client(object):
    client = None

    def __init__(self):
        self.client = SoapClient(
            soap_ns='soap11',
            location="https://webpay3g.orangepeople.cl:443/webpayserver/wswebpay/OneClickPaymentService",
            namespace="http://webservices.webpayserver.transbank.com/",
            trace=True)

    def request(self, action, xml, headerss):
        response_content = self.client.send('initInscription', xml)
        response = Response(response_content, action)
        return response
