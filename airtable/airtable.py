import json
import posixpath
import requests
import six
from collections import OrderedDict

API_URL = 'https://api.airtable.com/v%s/'
API_VERSION = '0'


class IsNotInteger(Exception):
    pass


class IsNotString(Exception):
    pass


def check_integer(n):
    if not n:
        return False
    elif not isinstance(n, six.integer_types):
        raise IsNotInteger('Expected an integer', n)
    else:
        return True


def check_string(s):
    if not s:
        return False
    elif not isinstance(s, six.string_types):
        raise IsNotString('Expected a string', s)
    else:
        return True


def create_payload(data):
    return {'fields': data}


class AirtableError(Exception):

    def __init__(self, error_type, message):
        super(AirtableError, self).__init__()
        # Examples of types are:
        #  TABLE_NOT_FOUND
        #  VIEW_NAME_NOT_FOUND
        self.type = error_type
        self.message = message

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.type, self.message)

    def __str__(self):
        return self.message or self.__class__.__name__


class Airtable(object):
    def __init__(self, base_id, api_key, dict_class=OrderedDict):
        """Create a client to connect to an Airtable Base.

        Args:
            - base_id: The ID of the base, e.g. "appA0CDAE34F"
            - api_key: The API secret key, e.g. "keyBAAE123C"
            - dict_class: the class to use to build dictionaries for returning
                  fields. By default the fields are kept in the order they were
                  returned by the API using an OrderedDict, but you can switch
                  to a simple dict if you prefer.
        """
        self.airtable_url = API_URL % API_VERSION
        self.base_url = posixpath.join(self.airtable_url, base_id)
        self.headers = {'Authorization': 'Bearer %s' % api_key}
        self._dict_class = dict_class

    def __request(self, method, url, params=None, payload=None):
        if method in ['POST', 'PUT', 'PATCH']:
            self.headers.update({'Content-type': 'application/json'})
        r = requests.request(method,
                             posixpath.join(self.base_url, url),
                             params=params,
                             data=payload,
                             headers=self.headers)
        if r.status_code == requests.codes.ok:
            return r.json(object_pairs_hook=self._dict_class)
        else:
            error_json = r.json().get('error', {})
            raise AirtableError(
                error_type=error_json.get('type', str(r.status_code)),
                message=error_json.get('message', json.dumps(r.json())))

    def get(
            self, table_name, record_id=None, limit=0, offset=None,
            filter_by_formula=None, view=None, max_records=0, fields=[]):
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
            if max_records and check_integer(max_records):
                params.update({'maxRecords': max_records})
            if fields and type(fields) is list:
                for field in fields:
                    check_string(field)
                params.update({'fields': fields})

        return self.__request('GET', url, params)

    def iterate(
            self, table_name, batch_size=0, filter_by_formula=None,
            view=None, max_records=0, fields=[]):
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
                table_name, limit=batch_size, offset=offset, max_records=max_records,
                fields=fields, filter_by_formula=filter_by_formula, view=view)
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

    def table(self, table_name):
        return Table(self, table_name)


class Table(object):
    def __init__(self, base_id, table_name, api_key=None, dict_class=OrderedDict):
        """Create a client to connect to an Airtable Table.

        Args:
            - base_id: The ID of the base, e.g. "appA0CDAE34F"
            - table_name: The name or ID of the table, e.g. "tbl123adfe4"
            - api_key: The API secret key, e.g. "keyBAAE123C"
            - dict_class: the class to use to build dictionaries for returning
                  fields. By default the fields are kept in the order they were
                  returned by the API using an OrderedDict, but you can switch
                  to a simple dict if you prefer.
        """
        self.table_name = table_name
        if isinstance(base_id, Airtable):
            self._client = base_id
            return
        self._client = Airtable(base_id, api_key, dict_class=dict_class)

    def get(
            self, record_id=None, limit=0, offset=None,
            filter_by_formula=None, view=None, max_records=0, fields=[]):
        return self._client.get(
            self.table_name, record_id, limit, offset, filter_by_formula, view, max_records, fields)

    def iterate(
            self, batch_size=0, filter_by_formula=None,
            view=None, max_records=0, fields=[]):
        return self._client.iterate(
            self.table_name, batch_size, filter_by_formula, view, max_records, fields)

    def create(self, data):
        return self._client.create(self.table_name, data)

    def update(self, record_id, data):
        return self._client.update(self.table_name, record_id, data)

    def update_all(self, record_id, data):
        return self._client.update_all(self.table_name, record_id, data)

    def delete(self, record_id):
        return self._client.delete(self.table_name, record_id)
