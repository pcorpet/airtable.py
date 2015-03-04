import json
import os
import requests

API_URL = 'https://api.airtable.com/v%s/'
API_VERSION = '0'

class IsNotInteger(Exception):
    pass

class IsNotString(Exception):
    pass

def checkInteger(n):
    if not n:
        return
    elif not isinstance(n, int):
        raise IsNotInteger('Expected an integer')
    else:
        return True

def checkString(s):
    if not s:
        return
    elif not isinstance(s, str):
        raise IsNotString('Expected a string')
    else:
        return True

class Airtable():
    def __init__(self, base_id, api_key):
        self.airtable_url = API_URL % API_VERSION
        self.base_url = os.path.join(self.airtable_url, base_id)
        self.headers = {'Authorization': 'Bearer %s' % api_key}

    def __request(self, method, url, params={}, payload=None):
        r = requests.request(method,
                             os.path.join(self.base_url, url),
                             params=params,
                             data=json.dumps(payload),
                             headers=self.headers)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return {'error': r.status_code}

    def get(self, table_name, id=None, limit=0, offset=None):
        params = {}
        if checkString(id):
            url = os.path.join(table_name, id)
        else:
            url = table_name
            if limit and checkInteger(limit):
                params.update({'limit': limit})
            if offset and checkString(offset):
                params.update({'offset': offset})
        return self.__request('GET', url, params)

    def delete(self, table_name, id):
        if checkString(table_name) and checkString(id):
            url = os.path.join(table_name, id)
            return self.__request('DELETE', url)