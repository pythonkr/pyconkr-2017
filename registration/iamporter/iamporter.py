# -*- coding: utf-8 -*-
import requests
import datetime


class IamporterError(Exception):
    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message
        return super(IamporterError, self).__init__('{code}: {message}'.format(code=code, message=message))

def get_access_token(api_key, api_secret):
    url = 'https://api.iamport.kr/users/getToken'
    response = requests.post(url, data=dict(
        imp_key=api_key,
        imp_secret=api_secret,
    ))

    if response.status_code != 200:
        raise IamporterError(response.status_code, response.content)

    # TODO : validate expire time
    result = response.json()

    if result['code'] is not 0:
        raise IamporterError(result['code'], result['message'])

    return result['response']['access_token']


class Iamporter(object):
    TOKEN_HEADER = 'X-ImpTokenHeader'

    def __init__(self, access_token):
        self._access_code = access_token

    def _set_default(self, data, headers):
        if not data:
            data = {}

        if not headers:
            headers = {}
        headers[self.TOKEN_HEADER] = self._access_code

        return data, headers

    def _parse_response(self, response):
        if response.status_code != 200 or not response.content:
            raise IamporterError(response.status_code, response.content)

        result = response.json()

        if result['code'] is not 0:
            raise IamporterError(result['code'], result['message'])

        return result['response']

    def _get(self, url, data=None, headers=None):
        data, headers = self._set_default(data, headers)
        response = requests.get(url, headers=headers, params=data)

        return self._parse_response(response)

    def _post(self, url, data=None, headers=None):
        data, headers = self._set_default(data, headers)
        response = requests.post(url, headers=headers, data=data)

        return self._parse_response(response)

    def onetime(self, **params):
        url = 'https://api.iamport.kr/subscribe/payments/onetime/'
        keys = ['token', 'merchant_uid', 'amount', 'vat', 'card_number', 'expiry', 'birth', 'pwd_2digit',
                'name', 'remember_me', 'customer_uid', 'buyer_name', 'buyer_email', ]
        data = {k: v for k, v in params.items() if k in keys}
        return self._post(url, data)

    def foreign(self, **params):
        url = 'https://api.iamport.kr/subscribe/payments/foreign/'
        keys = ['token', 'merchant_uid', 'amount', 'vat', 'card_number', 'expiry',
                'name', 'buyer_name', 'buyer_email', ]
        data = {k: v for k, v in params.items() if k in keys}
        return self._post(url, data)

    def cancel(self, **params):
        url = 'https://api.iamport.kr/payments/cancel/'
        keys = ['merchant_uid', 'reason', ]
        data = {k: v for k, v in params.items() if k in keys}
        return self._post(url, data)

    def find_by_merchant_uid(self, merchant_uid):
        url = 'https://api.iamport.kr/payments/find/{merchant_uid}'.format(merchant_uid=merchant_uid)
        return self._get(url)

    def get_paid_list(self, since, until=datetime.datetime.now()):
        url = 'https://api.iamport.kr/payments/status/{payment_status}'.format(payment_status='paid')
        since = int(since.strftime('%s'))
        until = int(until.strftime('%s'))
        data = {
                'from': since,
                'to': until,
                'page': 1,
               }
        full_list = []
        while True:
            result = self._get(url, data)
            full_list.extend(result['list'])
            if result['next'] != 0:
                data['page'] += 1
                continue
            else:
                break
        return full_list
