# -*- coding: utf-8 -*-
"""
A Translation module.

You can translate text using this module.
"""
import random
import typing
import json

import httpcore
import httpx
from httpx import Timeout

from google_trans import urls, utils
from google_trans.gtoken import TokenAcquirer
from google_trans.constants import (
    DEFAULT_CLIENT_SERVICE_URLS,
    DEFAULT_FALLBACK_SERVICE_URLS,
    DEFAULT_USER_AGENT, LANGCODES, LANGUAGES, SPECIAL_CASES,
    DEFAULT_RAISE_EXCEPTION, DUMMY_DATA
)

EXCLUDES = ('en', 'ca', 'fr')

RPC_ID = 'MkEWBc'

class Translator:
    """Google Translate ajax API implementation class

    You have to create an instance of Translator to use this API

    :param service_urls: google translate url list. URLs will be used randomly.
                         For example ``['translate.google.com', 'translate.google.co.kr']``
                         To preferably use the non webapp api, service url should be translate.googleapis.com
    :type service_urls: a sequence of strings

    :param user_agent: the User-Agent header to send when making requests.
    :type user_agent: :class:`str`

    :param proxies: proxies configuration.
                    Dictionary mapping protocol or protocol and host to the URL of the proxy
                    For example ``{'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}``
    :type proxies: dictionary

    :param timeout: Definition of timeout for httpx library.
                    Will be used for every request.
    :type timeout: number or a double of numbers
    :param proxies: proxies configuration.
                    Dictionary mapping protocol or protocol and host to the URL of the proxy
                    For example ``{'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}``
    :param raise_exception: if `True` then raise exception if smth will go wrong
    :param http2: whether to use HTTP2 (default: True)
    :param use_fallback: use a fallback method
    :type raise_exception: boolean
    """

    def __init__(self, service_urls=DEFAULT_CLIENT_SERVICE_URLS, user_agent=DEFAULT_USER_AGENT,
                 raise_exception=DEFAULT_RAISE_EXCEPTION,
                 proxies: typing.Dict[str, httpcore.SyncHTTPTransport] = None,
                 timeout: Timeout = None,
                 http2=True,
                 use_fallback=False):

        self.client = httpx.Client(http2=http2)
        if proxies is not None:  # pragma: nocover
            self.client.proxies = proxies

        self.client.headers.update({
            'User-Agent': user_agent,
            'Referer': 'https://translate.google.com',
        })

        if timeout is not None:
            self.client.timeout = timeout

        if use_fallback:
            self.service_urls = DEFAULT_FALLBACK_SERVICE_URLS
            self.client_type = 'gtx'
            pass
        else:
            # default way of working: use the defined values from user app
            self.service_urls = service_urls
            self.client_type = 'tw-ob'
            self.token_acquirer = TokenAcquirer(
                client=self.client, host=self.service_urls[0])

        self.raise_exception = raise_exception

    def _build_rpc_request(self, text: str, dest: str, src: str):
        return json.dumps([[
            [
                RPC_ID,
                json.dumps([[text, src, dest, True],[None]], separators=(',', ':')),
                None,
                'generic',
            ],
        ]], separators=(',', ':'))

    def _pick_service_url(self):
        if len(self.service_urls) == 1:
            return self.service_urls[0]
        return random.choice(self.service_urls)

    def _translate(self, text: str, dest: str, src: str):
        url = urls.TRANSLATE_RPC.format(host=self._pick_service_url())
        data = {
            'f.req': self._build_rpc_request(text, dest, src),
        }
        params = {
            'rpcids': RPC_ID,
            'bl': 'boq_translate-webserver_20201207.13_p0',
            'soc-app': 1,
            'soc-platform': 1,
            'soc-device': 1,
            'rt': 'c',
        }
        r = self.client.post(url, params=params, data=data)

        if r.status_code != 200 and self.raise_Exception:
            raise Exception('Unexpected status code "{}" from {}'.format(r.status_code, self.service_urls))

        return r.text, r

    def _translate_legacy(self, text, dest, src, override):
        token = ''  # dummy default value here as it is not used by api client
        if self.client_type == 'webapp':
            token = self.token_acquirer.do(text)

        params = utils.build_params(client=self.client_type, query=text, src=src, dest=dest,
                                    token=token, override=override)

        url = urls.TRANSLATE.format(host=self._pick_service_url())
        r = self.client.get(url, params=params)

        if r.status_code == 200:
            data = utils.format_json(r.text)
            return data, r

        if self.raise_exception:
            raise Exception('Unexpected status code "{}" from {}'.format(r.status_code, self.service_urls))

        DUMMY_DATA[0][0][0] = text
        return DUMMY_DATA, r

    def _parse_extra_data(self, data):
        response_parts_name_mapping = {
            0: 'translation',
            1: 'all-translations',
            2: 'original-language',
            5: 'possible-translations',
            6: 'confidence',
            7: 'possible-mistakes',
            8: 'language',
            11: 'synonyms',
            12: 'definitions',
            13: 'examples',
            14: 'see-also',
        }

        extra = {}

        for index, category in response_parts_name_mapping.items():
            extra[category] = data[index] if (
                index < len(data) and data[index]) else None

        return extra

    def translate(self, text: str, src='en', dest='en'):
        dest = dest.lower().split('_', 1)[0]
        src = src.lower().split('_', 1)[0]

        if src != 'auto' and src not in LANGUAGES:
            if src in SPECIAL_CASES:
                src = SPECIAL_CASES[src]
            elif src in LANGCODES:
                src = LANGCODES[src]
            else:
                raise ValueError('invalid source language')

        if dest not in LANGUAGES:
            if dest in SPECIAL_CASES:
                dest = SPECIAL_CASES[dest]
            elif dest in LANGCODES:
                dest = LANGCODES[dest]
            else:
                raise ValueError('invalid destination language')

        origin = text
        data, response = self._translate(text, dest, src)

        token_found = False
        square_bracket_counts = [0, 0]
        resp = ''
        for line in data.split('\n'):
            token_found = token_found or f'"{RPC_ID}"' in line[:30]
            if not token_found:
                continue

            is_in_string = False
            for index, char in enumerate(line):
                if char == '\"' and line[max(0, index - 1)] != '\\':
                    is_in_string = not is_in_string
                if not is_in_string:
                    if char == '[':
                        square_bracket_counts[0] += 1
                    elif char == ']':
                        square_bracket_counts[1] += 1

            resp += line
            if square_bracket_counts[0] == square_bracket_counts[1]:
                break

        data = json.loads(resp)
        parsed = json.loads(data[0][2])
        # not sure
        should_spacing = parsed[1][0][0][3]
        # translated_parts = list(map(lambda part: part[0] if len(part) >= 2 else [], parsed[1][0][0][5]))
        # translated = (' ' if should_spacing else '').join(map(lambda part: part, translated_parts))
        # print('translated .... ', translated)

        # return translated
        translated_parts = list(map( lambda part: part[0], parsed[1][0][0][5]) )


        translated = (' ' if should_spacing else '').join(map(lambda part: part, translated_parts))
        return translated
