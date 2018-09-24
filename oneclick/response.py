# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from pysimplesoap import xmlsec
import os

RESPONSE_CODE = {
    'Authorize': {
        '0': 'Aprobado.',
        '-1': 'La transacción ha sido rechazada, por favor contacta a tu banco para más información.',
        '-2': 'Ha ocurrido un error inesperado, por favor vuelve a intentar en unos minutos, si el error persiste contacta a tu banco.',
        '-3': 'Ha ocurrido un error al hacer la transacción, por favor contacta a tu banco para más información.',
        '-4': 'La transacción ha sido rechazada, por favor contacta a tu banco para más información.',
        '-5': 'La transacción ha sido rechazada porque la tasa es inválida.',
        '-6': 'Ha alcanzado el límite de transacciones mensuales, por favor contacta a tu banco para más información.',
        '-7': 'Ha alcanzado el límite de transacciones diarias, por favor contacta a tu banco para más información.',
        '-8': 'La transacción ha sido rechazada, por favor contacta a tu banco para más información.',
        '-97': 'Ha alcanzado el máximo monto diario de pagos, por favor contacta a tu banco para más información.',
        '-98': 'La transacción ha sido rechazada porque ha excedido el máximo monto de pago, por favor contacta a servicio al cliente.',
        '-99': 'La transacción ha sido rechazada porque ha excedido la máxima cantidad de pagos diarias.'
    },
    'default': {
        '0': 'Aprobado.',
        '-98': 'Ha ocurrido un error inesperado, por favor vuelve a intentar en unos minutos.'
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
        self.content = self._canonicalize(content)
        self.action = action
        self.xml_response = self.build_xml_response(content)
        self.validate()

    def build_xml_response(self, xml_string):
        try:
            return ET.fromstring(xml_string)
        except ParseError:
            return None

    def _canonicalize(self, xml):  # TODO: move to utils or document.py
        try:
            return xmlsec.canonicalize(xml)
        except:
            return None

    @property
    def tbk_key(self):
        if not self._tbk_key:
            self._tbk_key = xmlsec.x509_extract_rsa_public_key(open(os.getenv('TBK_PUBLIC_CRT')).read())
        return self._tbk_key

    @property
    def _signed_info(self):  # TODO: move to utils or document.py
        namespaces = ['{http://schemas.xmlsoap.org/soap/envelope/}Header',
                      '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security',
                      '{http://www.w3.org/2000/09/xmldsig#}Signature',
                      '{http://www.w3.org/2000/09/xmldsig#}SignedInfo']
        element = self.xml_response
        for ns in namespaces:
            element = element.findall(ns)[0]
        signed_info = ET.tostring(element)
        return self._canonicalize(signed_info)

    @property
    def _signature_value(self):
        namespaces = ['{http://schemas.xmlsoap.org/soap/envelope/}Header',
                      '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security',
                      '{http://www.w3.org/2000/09/xmldsig#}Signature',
                      '{http://www.w3.org/2000/09/xmldsig#}SignatureValue']

        element = self.xml_response
        for ns in namespaces:
            element = element.findall(ns)[0]
        signature_value = element.text
        return signature_value

    def _is_valid_signature(self):
        if self._testing:
            return True
        elif not os.getenv('TBK_PUBLIC_CRT'):  # tbk certificate undefined
            return True
        return xmlsec.rsa_verify(self._signed_info,
                                 self._signature_value,
                                 self.tbk_key, c14n_exc=True)

    def str2bool(self, bool_string):  # TODO: move to utils
        if bool_string.lower() == 'true':
            return True
        elif bool_string.lower() == 'false':
            return False
        raise TypeError

    @property
    def params(self):
        if not self._xml_result:
            result = {}
            for e in self.xml_response.findall('.//return'):
                for children in e.getchildren():
                    if self.action == 'codeReverseOneClick':
                        try:
                            result[children.tag] = self.str2bool(children.text)
                        except TypeError:
                            result[children.tag] = children.text
                    else:
                        result[children.tag] = children.text
                else:
                    if self.action == 'removeUser':
                        result['removed'] = self.str2bool(e.text)

            obj = {}
            for p in VALID_RESPONSE_PARAMS[self.action]:
                obj[p] = result.get(p)
                setattr(self, p, result.get(p))
            self._xml_result = obj
        return self._xml_result

    @property
    def xml_error(self):
        self._xml_error = None
        if not self._xml_error and self.xml_response:
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
        if not self.xml_response:
            self.error = 'SoapServerError'
            self.error_msg = 'invalid XML response'
            self.user_error_msg = 'Error al realizar la operación'
            self.extra = {}
        elif self.xml_error:
            self.error = 'SoapServerError'
            self.error_msg = self.xml_error['faultstring']
            self.user_error_msg = 'Error al realizar la operación'
            self.extra = self.xml_error
        elif not self._is_valid_signature():
            self.error = 'SecurityError'
            self.error_msg = 'invalid signature value'
            self.user_error_msg = 'Error al realizar la operación'
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

            elif self.action == 'codeReverseOneClick' and not self.params['reversed']:
                self.error = 'codeReverseOneClickError'
                self.error_msg = 'imposible revertir la compra'
                self.user_error_msg = self.error_msg
                self.extra = {'reversed': False}
