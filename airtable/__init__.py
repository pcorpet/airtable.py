from collections import OrderedDict
import json
import posixpath
from typing import Any, Generic, Mapping, TypeVar
import warnings

import requests
import six

API_URL = 'https://api.airtable.com/v%s/'
API_VERSION = '0'


class IsNotInteger(Exception):
    pass


class IsNotString(Exception):
    pass


def check_integer(integer):
    if not integer:
        return False
    if not isinstance(integer, six.integer_types):
        raise IsNotInteger('Expected an integer', integer)
    return True


def check_string(string):
    if not string:
        return False
    if not isinstance(string, six.string_types):
        raise IsNotString('Expected a string', string)
    return True


def create_payload(data):
    return {'fields': data}


_T = TypeVar('_T', bound=Mapping[str, Any])


class Record(Generic[_T]):

    def __init__(self):
        raise NotImplementedError(
            'This class is only used as a type of records returned by this module, however '
            'it should only be used as a type (see typing stubs) and not as an actual class.'
        )

    def __getitem__(self, key):
        pass

    def get(self, key, default=None):  # pylint-disable=invalid-name
        pass


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
        response = requests.request(
            method,
            posixpath.join(self.base_url, url),
            params=params,
            data=payload,
            headers=self.headers)
        if response.status_code == requests.codes.ok:
            return response.json(object_pairs_hook=self._dict_class)
        error_json = response.json().get('error', {})
        raise AirtableError(
            error_type=error_json.get('type', str(response.status_code)),
            message=error_json.get('message', json.dumps(response.json())))

    def get(  # pylint: disable=invalid-name
            self, table_name, record_id=None, limit=0, offset=None,
            filter_by_formula=None, view=None, max_records=0, fields=None):
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
            if fields and isinstance(fields, (list, tuple)):
                for field in fields:
                    check_string(field)
                # Duplicate a single field, https://github.com/josephbestjames/airtable.py/issues/47
                if len(fields) == 1:
                    fields = fields + fields
                params.update({'fields': fields})

        return self.__request('GET', url, params)

    def iterate(
            self, table_name, batch_size=0, filter_by_formula=None,
            view=None, max_records=0, fields=None):
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
        assert check_string(table_name)
        payload = create_payload(data)
        return self.__request('POST', table_name, payload=json.dumps(payload))

    def update(self, table_name, record_id, data):
        assert check_string(table_name) and check_string(record_id)
        url = posixpath.join(table_name, record_id)
        payload = create_payload(data)
        return self.__request('PATCH', url, payload=json.dumps(payload))

    def update_all(self, table_name, record_id, data):
        assert check_string(table_name) and check_string(record_id)
        url = posixpath.join(table_name, record_id)
        payload = create_payload(data)
        return self.__request('PUT', url, payload=json.dumps(payload))

    def delete(self, table_name, record_id):
        assert check_string(table_name) and check_string(record_id)
        url = posixpath.join(table_name, record_id)
        return self.__request('DELETE', url)

    def table(self, table_name):
        return Table(self, table_name)


class Table(Generic[_T]):
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

    def get(  # pylint:disable=invalid-name
            self, record_id=None, limit=0, offset=None,
            filter_by_formula=None, view=None, max_records=0, fields=None):
        return self._client.get(
            self.table_name, record_id, limit, offset, filter_by_formula, view, max_records, fields)

    def iterate(
            self, batch_size=0, filter_by_formula=None,
            view=None, max_records=0, fields=None):
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


class _ProxyModule(object):

    def _this(self):
        warnings.warn(
            'airtable.airtable is deprecated, import airtable directly.',
            DeprecationWarning)
        return __import__(__name__)

    def __eq__(self, other):
        return other is self or other is self._this()

    def __str__(self):
        return str(self._this())

    def __repr__(self):
        return repr(self._this())

    def __dir__(self):
        return dir(self._this())

    def __getattr__(self, name):
        if name == '__members__':
            return dir(self._get_current_object())
        return getattr(self._this(), name)

    def __setattr__(self, name, value):
        return setattr(self._this(), name, value)

    def __delattr__(self, name):
        return delattr(self._this(), name)


# Access to this module through deprecated "import airtable from airtable".
airtable = _ProxyModule()
