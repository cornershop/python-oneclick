# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

RESPONSE_CODE = {
    'authorize': {
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
    'removeUser': ['removed']  # TODO: fix here
}


class Validator(object):
    action = None
    content = None
    xml_response = None
    errors = None
    _xml_result = None
    _xml_error = None

    def __init__(self, content, action):
        self.errors = []
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
                self._xml_error = {'faultcode': faultcode[0].text, 'faultstring': faultstring[0].text}
        return self._xml_error

    def is_valid(self):
        if self.errors:
            return False
        return True

    @property
    def response_code(self):
        if self.xml_result and 'responseCode' in self.xml_result:
            return self.xml_result['responseCode']
        return None

    def response_code_display(self):
        if self.action in RESPONSE_CODE and self.response_code in RESPONSE_CODE[self.action]:
            return RESPONSE_CODE[self.action][self.response_code]
        elif self.response_code in RESPONSE_CODE['default']:
            RESPONSE_CODE['default'][self.response_code]
        else:
            return self.response_code

    def validate(self):
        if self.xml_error:
            self.errors.append('error')
        else:
            if self.action in ['finishInscription', 'Authorize'] and int(self.response_code) != 0:
                self.errors.append(self.response_code_display())

            elif self.action == 'removeUser' and not self.xml_result['removed']:  # TODO
                self.errors.append('imposible eliminar la inscripción')

            elif self.action == 'codeReverseOneClick' and self.xml_result['reversed'] != 'true':
                self.errors.append('imposible revertir la compra')
