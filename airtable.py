import json
import os
import requests

API_URL = 'https://api.airtable.com/v%s/'
API_VERSION = '0'

class IsNotInteger(Exception):
    pass

class IsNotString(Exception):
    pass

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
        print r.request.headers
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return {'error': r.status_code}

    def get(self, table_name, id=None, limit=0, offset=None):
        params = {}
        if id:
            url = os.path.join(table_name, id)
        else:
            url = table_name
            if limit:
                if not isinstance(limit, int):
                    raise IsNotInteger('Limit is not an integer')
                params.update({'limit': limit})
            if offset:
                if not isinstance(offset, str):
                    raise IsNotString('Offset is not a string')
                params.update({'offset': offset})
        return self.__request('GET', url, params)

    def delete(self, table_name, id):
        url = os.path.join(table_name, id)
        return self.__request('DELETE', url)