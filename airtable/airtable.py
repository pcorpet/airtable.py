import json
import posixpath 
import requests
from collections import OrderedDict

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


class Airtable(object):
    def __init__(self, base_id, api_key):
        self.airtable_url = API_URL % API_VERSION
        self.base_url = posixpath.join(self.airtable_url, base_id)
        self.headers = {'Authorization': 'Bearer %s' % api_key}

    def __request(self, method, url, params=None, payload=None):
        if method in ['POST', 'PUT', 'PATCH']:
            self.headers.update({'Content-type': 'application/json'})
        r = requests.request(method,
                             posixpath.join(self.base_url, url),
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

    def get(
            self, table_name, record_id=None, limit=0, offset=None,
            filter_by_formula=None, view=None):
        params = {}
        if check_string(record_id):
            url = posixpath.join(table_name, record_id)
        else:
            url = table_name
            if limit and check_integer(limit):
                params.update({'pageSize': limit})
            if offset and check_string(offset):
                params.update({'offset': offset})
            if filter_by_formula is not None:
                params.update({'filterByFormula': filter_by_formula})
            if view is not None:
                params.update({'view': view})
        return self.__request('GET', url, params)

    def iterate(
            self, table_name, batch_size=0, filter_by_formula=None, view=None):
        """Iterate over all records of a table.

        Args:
            table_name: the name of the table to list.
            batch_size: the number of records to fetch per request. The default
                (0) is using the default of the API which is (as of 2016-09)
                100. Note that the API does not allow more than that (but
                allow for less).
            filter_by_formula: a formula used to filter records. The formula
                will be evaluated for each record, and if the result is not 0,
                false, "", NaN, [], or #Error! the record will be included in
                the response. If combined with view, only records in that view
                which satisfy the formula will be returned.
            view: the name or ID of a view in the table. If set, only the
                records in that view will be returned. The records will be
                sorted according to the order of the view.
        Yields:
            A dict for each record containing at least three fields: "id",
            "createdTime" and "fields".
        """
        offset = None
        while True:
            response = self.get(
                table_name, limit=batch_size, offset=offset,
                filter_by_formula=filter_by_formula, view=view)
            for record in response.pop('records'):
                yield record
            if 'offset' in response:
                offset = response['offset']
            else:
                break

    def create(self, table_name, data):
        if check_string(table_name):
            payload = create_payload(data)
            return self.__request('POST', table_name,
                                  payload=json.dumps(payload))

    def update(self, table_name, record_id, data):
        if check_string(table_name) and check_string(record_id):
            url = posixpath.join(table_name, record_id)
            payload = create_payload(data)
            return self.__request('PATCH', url,
                                  payload=json.dumps(payload))

    def update_all(self, table_name, record_id, data):
        if check_string(table_name) and check_string(record_id):
            url = posixpath.join(table_name, record_id)
            payload = create_payload(data)
            return self.__request('PUT', url,
                                  payload=json.dumps(payload))

    def delete(self, table_name, record_id):
        if check_string(table_name) and check_string(record_id):
            url = posixpath.join(table_name, record_id)
            return self.__request('DELETE', url)
