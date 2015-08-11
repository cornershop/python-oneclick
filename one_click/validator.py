# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

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


class Validator(object):
    action = None
    content = None
    xml_response = None
    error = None
    error_msg = ''
    user_error_msg = ''
    extra = {}
    _xml_result = None
    _xml_error = None

    def __init__(self, content, action):
        self.error = None
        self.content = content
        self.action = action
        self.xml_response = self.build_xml_response(content)
        self.validate()

    def build_xml_response(self, xml_string):
        return ET.fromstring(xml_string)

    @property
    def xml_result(self):
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
        if self.xml_result and 'responseCode' in self.xml_result:
            return str(self.xml_result['responseCode'])
        return None

    def response_code_display(self):
        if self.action in RESPONSE_CODE and self.response_code in RESPONSE_CODE[self.action]:
            return RESPONSE_CODE[self.action][self.response_code]
        elif self.response_code in RESPONSE_CODE['default']:
            return RESPONSE_CODE['default'][self.response_code]
        else:
            return self.response_code

    def validate(self):
        if self.xml_error:
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

            elif self.action == 'removeUser' and not self.xml_result['removed']:
                self.error = 'removeUserError'
                self.error_msg = 'imposible eliminar la inscripción'
                self.user_error_msg = self.error_msg
                self.extra = {'removed': False}

            elif self.action == 'codeReverseOneClick' and self.xml_result['reversed'] != 'true':
                self.error = 'codeReverseOneClickError'
                self.error_msg = 'imposible revertir la compra'
                self.user_error_msg = self.error_msg
                self.extra = {'reversed': False}
