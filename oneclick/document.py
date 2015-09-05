from OpenSSL import crypto
import arrow
import md5
import rsa
import os
import base64

SIGN_ENV_TMPL = """<ds:SignedInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod><ds:Reference URI="#%(body_id)s"><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod><ds:DigestValue>%(digest_value)s</ds:DigestValue></ds:Reference></ds:SignedInfo>"""

XML_TMPL = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Header><wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" SOAP-ENV:mustUnderstand="1"><ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod><ds:Reference URI="#%(body_id)s"><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod><ds:DigestValue>%(digest_value)s</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>%(signature_value)s</ds:SignatureValue><ds:KeyInfo><wsse:SecurityTokenReference><ds:X509Data><ds:X509IssuerSerial><ds:X509IssuerName>%(issuer_name)s</ds:X509IssuerName><ds:X509SerialNumber>%(serial_number)s</ds:X509SerialNumber></ds:X509IssuerSerial></ds:X509Data></wsse:SecurityTokenReference></ds:KeyInfo></ds:Signature></wsse:Security></SOAP-ENV:Header><SOAP-ENV:Body xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="%(body_id)s"><ns1:%(action)s xmlns:ns1="http://webservices.webpayserver.transbank.com/"><arg0>%(params)s</arg0></ns1:%(action)s></SOAP-ENV:Body></SOAP-ENV:Envelope>"""

BODY_TMPL = """<SOAP-ENV:Body xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="%(body_id)s"><ns1:%(action)s xmlns:ns1="http://webservices.webpayserver.transbank.com/"><arg0>%(params)s</arg0></ns1:%(action)s></SOAP-ENV:Body>"""


class Document(object):
    _key = None
    _cert = None
    _x509 = None
    _action = None
    _params = None
    doc = None

    def __init__(self, action, params):
        self._action = action
        self._params = params
        self.doc = self.build_doc()

    @property
    def key(self):
        if not self._key:
            self._key = os.getenv('TBK_COMMERCE_KEY')
        return self._key

    @property
    def cert(self):
        if not self._cert:
            self._cert = os.getenv('TBK_COMMERCE_CRT')
        return self._cert

    @property
    def x509(self):
        if not self._x509:
            self._x509 = crypto.load_certificate(crypto.FILETYPE_PEM, 
                                                 open(self.cert).read())
        return self._x509

    def get_issuer_name(self):
        issuer = self.x509.get_issuer()
        component_list = []
        for component in issuer.get_components():
            component_list.append('{}={}'.format(component[0], component[1]))
        return ", ".join(component_list)
        
    def get_serial_number(self):
        return str(self.x509.get_serial_number())

    def get_digest_value(self, xml, c14n_exc=True):
        return base64.b64encode(rsa.pkcs1._hash(xml, 'SHA-1'))

    def get_body_id(self):
        m = md5.new()
        m.update("{}{}{}".format(self._action, self._params,
                 arrow.now().format('YYYY-MM-DD HH:mm:ss ZZ')))
        return m.hexdigest()

    def rsa_sign(self, xml):
        with open(self.key) as privatefile:
            keydata = privatefile.read()
            key = rsa.PrivateKey.load_pkcs1(keydata)
            signature = rsa.sign(xml, key, 'SHA-1')
            return base64.b64encode(signature)

    def build_params_xml(self, params):
        params_xml = ""
        for k, v in params.items():
            params_xml += '<{0}>{1}</{0}>'.format(k, v)
        return params_xml

    def build_doc(self):
        body_id = self.get_body_id()
        # 1) build body
        body_params = self.build_params_xml(self._params)
        params = {'action': self._action, 'params': body_params, 'body_id': body_id}
        body = BODY_TMPL % params

        # 2) firm with body
        digest_value = self.get_digest_value(body, True)

        # 3) assign
        xml_to_sign = SIGN_ENV_TMPL % {'digest_value': digest_value, 'body_id': body_id}
        signature_value = self.rsa_sign(xml=xml_to_sign)
        # get params
        params = {'signature_value': signature_value, 'issuer_name': self.get_issuer_name(),
                  'serial_number': self.get_serial_number(), 'digest_value': digest_value,
                  'body_id': body_id, 'action': self._action, 'params': body_params}

        # 4) build headers
        return XML_TMPL % params
