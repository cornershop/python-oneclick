from pysimplesoap.client import SoapClient, SoapFault, SimpleXMLElement
import sys
from validator import Validator


class Client(object):
    client = None

    def __init__(self):
        self.client = SoapClient(
            soap_ns='soap11',
            location="https://webpay3g.orangepeople.cl:443/webpayserver/wswebpay/OneClickPaymentService",
            namespace="http://webservices.webpayserver.transbank.com/",
            trace=True)

    def send(self, method, xml):
        """Send SOAP request using HTTP"""
        http_method = str('POST')
        location = str(self.client.location)
        headers = {
            'Content-type': 'application/soap+xml; charset=utf-8',
            'Content-length': str(len(xml)),
        }
        headers.update(self.http_headers)
        if sys.version < '3':
            # Ensure http_method, location and all headers are binary to prevent
            # UnicodeError inside httplib.HTTPConnection._send_output.
            # httplib in python3 do the same inside itself, don't need to convert it here
            headers = dict((str(k), str(v)) for k, v in headers.items())
        response, content = self.client.http.request(
            location, http_method, body=xml, headers=headers)
        self.response = response

        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print "RESPONSE::::::::"
        print '\n'.join(["%s: %s" % (k, v) for k, v in response.items()])
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print "content::::::::"
        print content
        print dir(content)

        self.client.content = content
        content_xml = SimpleXMLElement(content)
        #print content_xml

        print '\n'.join(["%s: %s" % (k, v) for k, v in response.items()])
        return content

    def request(self, action, xml, headerss):
        response_content = self.client.send('initInscription', xml)
        v = Validator(response_content, action)
        return v.xml_result

