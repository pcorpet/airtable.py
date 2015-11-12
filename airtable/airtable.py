from collections import OrderedDict
import json
import os
import requests

API_URL = 'https://api.airtable.com/v%s/'
API_VERSION = '0'


class IsNotInteger(Exception):
    pass


class IsNotString(Exception):
    pass


def check_integer(n):
    if not n:
        return
    elif not isinstance(n, int):
        raise IsNotInteger('Expected an integer')
    else:
        return True


def check_string(s):
    if not s:
        return
    elif not isinstance(s, str):
        raise IsNotString('Expected a string')
    else:
        return True


def create_payload(data):
    return {'fields': data}


class Airtable():
    def __init__(self, base_id, api_key):
        self.airtable_url = API_URL % API_VERSION
        self.base_url = os.path.join(self.airtable_url, base_id)
        self.headers = {'Authorization': 'Bearer %s' % api_key}

    def __request(self, method, url, params=None, payload=None):
        if method in ['POST', 'PUT', 'PATCH']:
            self.headers.update({'Content-type': 'application/json'})
        r = requests.request(method,
                             os.path.join(self.base_url, url),
                             params=params,
                             data=payload,
                             headers=self.headers)
        if r.status_code == requests.codes.ok:
            return r.json(object_pairs_hook=OrderedDict)
        else:
            try:
                message = None
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                message = e.message
            return {
                'error': dict(code=r.status_code, message=message)
            }

    def get(self, table_name, record_id=None, limit=0, offset=None):
        params = {}
        if check_string(record_id):
            url = os.path.join(table_name, record_id)
        else:
            url = table_name
            if limit and check_integer(limit):
                params.update({'limit': limit})
            if offset and check_string(offset):
                params.update({'offset': offset})
        return self.__request('GET', url, params)

    def create(self, table_name, data):
        if check_string(table_name):
            payload = create_payload(data)
            return self.__request('POST', table_name,
                                  payload=json.dumps(payload))

    def update(self, table_name, record_id, data):
        if check_string(table_name) and check_string(record_id):
            url = os.path.join(table_name, record_id)
            payload = create_payload(data)
            return self.__request('PATCH', url,
                                  payload=json.dumps(payload))

    def update_all(self, table_name, record_id, data):
        if check_string(table_name) and check_string(record_id):
            url = os.path.join(table_name, record_id)
            payload = create_payload(data)
            return self.__request('PUT', url,
                                  payload=json.dumps(payload))

    def delete(self, table_name, record_id):
        if check_string(table_name) and check_string(record_id):
            url = os.path.join(table_name, record_id)
            return self.__request('DELETE', url)
