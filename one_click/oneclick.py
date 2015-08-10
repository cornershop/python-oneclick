from document import Document
from client import Client


class OneClick(object):
    client = None
    _key = None
    _cert = None

    def __init__(self, key, cert):
        self.client = Client()
        self._key = key
        self._cert = cert

    def init_inscription(self, email, response_url, username):
        params = {'email': email, 'username': username, 'responseURL': response_url}
        d = Document(key=self._key, cert=self._cert, action='initInscription', params=params)
        response = self.client.request('initInscription', d.doc, {})
        return response

    def finish_inscription(self, token):
        params = {'token': token}
        d = Document(key=self._key, cert=self._cert, action='finishInscription', params=params)
        response = self.client.request('finishInscription', d.doc, {})
        return response

    def authorize(self, amount, tbk_user, username, buy_order):
        params = {'amount': amount, 'tbkUser': tbk_user,
                  'username': username, 'buyOrder': buy_order}
        d = Document(key=self._key, cert=self._cert, action='Authorize', params=params)
        response = self.client.request('Authorize', d.doc, {})
        return response

    def reverse(self, buy_order):
        params = {'buyOrder': buy_order}
        d = Document(key=self._key, cert=self._cert, action='codeReverseOneClick', params=params)
        response = self.client.request('codeReverseOneClick', d.doc, {})
        return response

    def remove_user(self, tbk_user, username):
        params = {'tbkUser': tbk_user, 'username': username}
        d = Document(key=self._key, cert=self._cert, action='removeUser', params=params)
        response = self.client.request('removeUser', d.doc, {})
        return response
