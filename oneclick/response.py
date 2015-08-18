# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from pysimplesoap import xmlsec
from M2Crypto import RSA, EVP
import base64
import os

RESPONSE_CODE = {
    'Authorize': {
        '0': 'aprobado',
        '-1': 'rechazo',
        '-2': 'rechazo',
        '-3': 'rechazo',
        '-4': 'rechazo',
        '-5': 'rechazo',
        '-6': 'rechazo',
        '-7': 'rechazo',
        '-8': 'rechazo',
        '-97': 'limites Oneclick, máximo monto diario de pago excedido',
        '-98': 'limites Oneclick, máximo monto de pago excedido',
        '-99': 'limites Oneclick, máxima cantidad de pagos diarios excedido'
    },
    'default': {
        '0': 'aprobado',
        '-98': 'Error'
    }
}

VALID_RESPONSE_PARAMS = {
    'Authorize': ['authorizationCode', 'creditCardType',
                  'last4CardDigits', 'responseCode', 'transactionId'],
    'initInscription': ['token', 'urlWebpay'],
    'finishInscription': ['authCode', 'creditCardType', 'last4CardDigits',
                          'responseCode', 'tbkUser'],
    'codeReverseOneClick': ['reverseCode', 'reversed'],
    'removeUser': ['removed']
}


class Response(object):
    action = None
    content = None
    xml_response = None
    error = None
    error_msg = ''
    user_error_msg = ''
    extra = {}
    _xml_result = None
    _xml_error = None
    _tbk_key = None
    _testing = None

    def __init__(self, content, action, testing=False):
        self.error = None
        self._testing = testing
        self.content = content
        self.action = action
        self.xml_response = self.build_xml_response(content)
        self.validate()

    def build_xml_response(self, xml_string):
        return ET.fromstring(xml_string)

    def _canonicalize(self, xml):  # TODO: move to utils or document.py
        return xmlsec.canonicalize(xml)

    @property
    def _signed_info(self):  # TODO: move to utils or document.py
        namespaces = ['{http://schemas.xmlsoap.org/soap/envelope/}Header', 
                      '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security', 
                      '{http://www.w3.org/2000/09/xmldsig#}Signature', 
                      '{http://www.w3.org/2000/09/xmldsig#}SignedInfo'
        ]
        element = self.xml_response
        for ns in namespaces:
            element = element.findall(ns)[0]
        signed_info = ET.tostring(element)
        return self._canonicalize(signed_info)

    @property
    def tbk_key(self):
        if not self._tbk_key:
            self._tbk_key = xmlsec.x509_extract_rsa_public_key(open(os.getenv('TBK_PUBLIC_CRT')).read())
        return self._tbk_key

    @property
    def _signature_value(self):
        namespaces = ['{http://schemas.xmlsoap.org/soap/envelope/}Header', 
                      '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security', 
                      '{http://www.w3.org/2000/09/xmldsig#}Signature', 
                      '{http://www.w3.org/2000/09/xmldsig#}SignatureValue'
        ]
        element = self.xml_response
        for ns in namespaces:
            element = element.findall(ns)[0]
        signature_value = element.text
        return signature_value

    def _is_valid_signature(self):
        if self._testing:
            return True 
        return xmlsec.rsa_verify(self._signed_info, 
                                 self._signature_value, 
                                 self.tbk_key, c14n_exc=True)

    @property
    def params(self):
        if not self._xml_result:
            result = {}

            for e in self.xml_response.findall('.//return'):
                for children in e.getchildren():
                    result[children.tag] = children.text
                else:
                    result['removed'] = bool(e.text)
            if result:
                params = VALID_RESPONSE_PARAMS[self.action]
                obj = {}
                for p in params:
                    if p in result:
                        obj[p] = result[p]
                    else:
                        obj[p] = None
                self._xml_result = obj
        return self._xml_result

    @property
    def xml_error(self):
        self._xml_error = None
        if not self._xml_error:
            faultcode = self.xml_response.findall('.//faultcode')
            faultstring = self.xml_response.findall('.//faultstring')
            if faultcode and faultstring:
                self._xml_error = {'faultcode': faultcode[0].text,
                                   'faultstring': faultstring[0].text}
        return self._xml_error

    def is_valid(self):  # True or False if any errors occurred (exceptions included)
        if self.error:
            return False
        return True

    @property
    def response_code(self):
        if self.params and 'responseCode' in self.params:
            return str(self.params['responseCode'])
        return None

    def response_code_display(self):
        if self.action in RESPONSE_CODE and self.response_code in RESPONSE_CODE[self.action]:
            return RESPONSE_CODE[self.action][self.response_code]
        elif self.response_code in RESPONSE_CODE['default']:
            return RESPONSE_CODE['default'][self.response_code]
        else:
            return self.response_code

    def validate(self):
        if not self._is_valid_signature():
            self.error = 'SecurityError'
            self.error_msg = 'invalid signature value'
            self.user_error_msg = ''
            self.extra = self.xml_error
        elif self.xml_error:
            self.error = 'SoapServerError'
            self.error_msg = self.xml_error['faultstring']
            self.user_error_msg = ''
            self.extra = self.xml_error
        else:
            if self.action in ['finishInscription', 'Authorize'] and int(self.response_code) != 0:
                self.error = '{}Error'.format(self.action)
                self.error_msg = self.response_code_display()
                self.user_error_msg = self.error_msg
                self.extra = {'response_code': self.response_code}

            elif self.action == 'removeUser' and not self.params['removed']:
                self.error = 'removeUserError'
                self.error_msg = 'imposible eliminar la inscripción'
                self.user_error_msg = self.error_msg
                self.extra = {'removed': False}

            elif self.action == 'codeReverseOneClick' and self.params['reversed'] != 'true':
                self.error = 'codeReverseOneClickError'
                self.error_msg = 'imposible revertir la compra'
                self.user_error_msg = self.error_msg
                self.extra = {'reversed': False}
