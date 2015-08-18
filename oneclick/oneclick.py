from document import Document
from request import Request
from client import Client
from .logging import logger


class OneClick(object):
    client = None

    def __init__(self, testing=False):
        self.client = Client(testing)

    def init_inscription(self, email, response_url, username):
        params = {'email': email, 'username': username, 'responseURL': response_url}
        request = Request(**params)
        d = Document(action='initInscription', params=params)
        response = self.client.request('initInscription', d.doc)
        logger.generic('init_inscription', request, response)
        return response

    def finish_inscription(self, token):
        params = {'token': token}
        request = Request(**params)
        d = Document(action='finishInscription', params=params)
        response = self.client.request('finishInscription', d.doc)
        logger.generic('finish_inscription', request, response)
        return response

    def authorize(self, amount, tbk_user, username, buy_order):
        params = {'amount': amount, 'tbkUser': tbk_user,
                  'username': username, 'buyOrder': buy_order}
        request = Request(**params)
        d = Document(action='authorize', params=params)
        response = self.client.request('Authorize', d.doc)
        logger.generic('authorize', request, response)
        return response

    def reverse(self, buy_order):
        params = {'buyorder': buy_order}
        request = Request(**params)
        d = Document(action='codeReverseOneClick', params=params)
        response = self.client.request('codeReverseOneClick', d.doc)
        logger.generic('reverse', request, response)
        return response

    def remove_user(self, tbk_user, username):
        params = {'tbkUser': tbk_user, 'username': username}
        request = Request(**params)
        d = Document(action='removeUser', params=params)
        response = self.client.request('removeUser', d.doc)
        logger.generic('remove_user', request, response)
        return response
