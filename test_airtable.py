import airtable
import mock
import requests
from typing import Any, Dict
import unittest

FAKE_TABLE_NAME = 'TableName'
FAKE_BASE_ID = 'app12345'
FAKE_API_KEY = 'fake_api_key'


class TestAirtable(unittest.TestCase):
    def setUp(self):
        self.base_id = FAKE_BASE_ID
        self.api_key = FAKE_API_KEY
        self.airtable = airtable.Airtable(self.base_id, self.api_key)

    def get(self, *args, **kwargs):
        return self.airtable.get(FAKE_TABLE_NAME, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.airtable.delete(FAKE_TABLE_NAME, *args, **kwargs)

    def iterate(self, *args, **kwargs):
        return self.airtable.iterate(FAKE_TABLE_NAME, *args, **kwargs)

    def test_build_base_url(self):
        self.assertEqual(self.airtable.base_url,
                         'https://api.airtable.com/v0/app12345')

    def test_build_headers(self):
        self.assertEqual(self.airtable.headers['Authorization'],
                         'Bearer fake_api_key')

    @mock.patch.object(requests, 'request')
    def test_get_all(self, mock_request):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'records': [
                {
                    'id': 'reccA6yaHKzw5Zlp0',
                    'fields': {
                        'Name': 'John',
                        'Number': '(987) 654-3210'
                    }
                },
                {
                    'id': 'reccg3Kke0QvTDW0H',
                    'fields': {
                        'Name': 'Nico',
                        'Number': '(123) 222-1131'
                    }
                }
            ],
            'offset': 'reccg3Kke0QvTDW0H'
        }
        mock_request.return_value = mock_response
        res = self.get()
        self.assertEqual(len(res['records']), 2)
        self.assertEqual(res['offset'], 'reccg3Kke0QvTDW0H')

    @mock.patch.object(requests, 'request')
    def test_order_of_fields_is_preserved(self, mock_request):
        mock_response = requests.Response()
        mock_response.status_code = 200

        # Set the text content of the response to a JSON string so we can test
        # how it gets deserialized
        mock_response._content = b'''{
            "records": [
                {
                    "id": "reccA6yaHKzw5Zlp0",
                    "fields": {
                        "a": 1,
                        "b": 2,
                        "c": 3,
                        "d": 4,
                        "e": 5,
                        "f": 6,
                        "g": 7,
                        "h": 8,
                        "i": 9,
                        "j": 10,
                        "k": 11,
                        "l": 12,
                        "m": 13
                    }
                },
                {
                    "id": "reccg3Kke0QvTDW0H",
                    "fields": {
                        "n": 14,
                        "o": 15,
                        "p": 16,
                        "q": 17,
                        "r": 18,
                        "s": 19,
                        "t": 20,
                        "u": 21,
                        "v": 22,
                        "w": 23,
                        "x": 24,
                        "y": 25,
                        "z": 26
                    }
                }
            ]
        }'''
        mock_response.encoding = 'utf-8'

        mock_request.return_value = mock_response
        r = self.airtable.get(FAKE_TABLE_NAME)
        self.assertEqual(list(r['records'][0]['fields'].keys()), list(u'abcdefghijklm'))
        self.assertEqual(list(r['records'][1]['fields'].keys()), list(u'nopqrstuvwxyz'))

    @mock.patch.object(requests, 'request')
    def test_get_by_id(self, mock_request):
        fake_id = 'reccA6yaHKzw5Zlp0'
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'reccA6yaHKzw5Zlp0',
            'fields': {
                'Name': 'John',
                'Number': '(987) 654-3210'
            }
        }
        mock_request.return_value = mock_response
        r = self.get(fake_id)
        self.assertEqual(r['id'], fake_id)

    @mock.patch.object(requests, 'request')
    def test_get_not_found(self, mock_request):
        mock_response = mock.MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'error': {
                'type': 'TABLE_NOT_FOUND',
                'message': 'Could not find table %s in application %s' % (
                    FAKE_TABLE_NAME, FAKE_BASE_ID),
            },
        }
        mock_request.return_value = mock_response
        with self.assertRaises(airtable.AirtableError) as error:
            self.get('123')
        self.assertEqual('TABLE_NOT_FOUND', error.exception.type)

    @mock.patch.object(requests, 'request')
    def test_get_view(self, mock_request):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'records': []}
        mock_request.return_value = mock_response

        r = self.get(view='My view')
        mock_request.assert_called_once_with(
            'GET', 'https://api.airtable.com/v0/app12345/TableName',
            data=None, headers={'Authorization': 'Bearer fake_api_key'},
            params={'view': 'My view'})

    @mock.patch.object(requests, 'request')
    def test_get_filter_by_formula(self, mock_request):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'records': []}
        mock_request.return_value = mock_response

        r = self.get(filter_by_formula="{title} = ''")
        mock_request.assert_called_once_with(
            'GET', 'https://api.airtable.com/v0/app12345/TableName',
            data=None, headers={'Authorization': 'Bearer fake_api_key'},
            params={'filterByFormula': "{title} = ''"})

    def test_invalid_get(self):
        with self.assertRaises(airtable.IsNotString):
            self.get(123)
            self.get(offset=123)
        with self.assertRaises(airtable.IsNotInteger):
            self.get(limit='1')

    @mock.patch.object(requests, 'request')
    def test_delete(self, mock_request):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'deleted': True,
            'id': '1234'
        }
        mock_request.return_value = mock_response
        r = self.delete('1234')
        self.assertTrue(r['deleted'])
        self.assertEqual(r['id'], '1234')

    def test_invalid_delete(self):
        with self.assertRaises(airtable.IsNotString):
            self.delete(123)

    @mock.patch.object(requests, 'request')
    def test_iterate(self, mock_request):
        mock_response1 = mock.MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'records': [
                {
                    'id': 'reccA6yaHKzw5Zlp0',
                    'fields': {
                        'Name': 'John',
                        'Number': '(987) 654-3210'
                    }
                },
                {
                    'id': 'reccg3Kke0QvTDW0H',
                    'fields': {
                        'Name': 'Nico',
                        'Number': '(123) 222-1131'
                    }
                }
            ],
            'offset': 'reccg3Kke0QvTDW0H'
        }
        mock_response2 = mock.MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'records': [
                {
                    'id': 'reccA23fSERw5Zlp0',
                    'fields': {
                        'Name': 'Ron',
                        'Number': '(987) 654-3210'
                    }
                },
            ],
        }
        mock_request.side_effect = [mock_response1, mock_response2]
        results = list(self.iterate())
        self.assertEqual(
            ['John', 'Nico', 'Ron'], [r.get('fields', {}).get('Name') for r in results])


class TestTableFromBase(TestAirtable):

    def setUp(self):
        super(TestTableFromBase, self).setUp()
        self.table = self.airtable.table(FAKE_TABLE_NAME)

    def get(self, *args, **kwargs):
        return self.table.get(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.table.delete(*args, **kwargs)

    def iterate(self, *args, **kwargs):
        return self.table.iterate(*args, **kwargs)


class TestTableFromConfig(TestAirtable):

    def setUp(self):
        super(TestTableFromConfig, self).setUp()
        self.table = airtable.Table(self.base_id, FAKE_TABLE_NAME, api_key=FAKE_API_KEY)

    def get(self, *args, **kwargs):
        return self.table.get(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.table.delete(*args, **kwargs)

    def iterate(self, *args, **kwargs):
        return self.table.iterate(*args, **kwargs)

    @mock.patch.object(requests, 'request')
    def test_typed_table(self, mock_request):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'records': [
                {
                    'id': 'reccA23fSERw5Zlp0',
                    'fields': {
                        'Name': 3,
                        'Number': 4
                    }
                },
            ],
        }
        mock_request.return_value = mock_response

        table = airtable.Table[Dict[str, int]](
            self.base_id, FAKE_TABLE_NAME, api_key=FAKE_API_KEY)
        response = table.get()
        self.assertEqual(response['records'][0]['fields'], {'Name': 3, 'Number': 4})


# This line is here only to check that Python code supports having the Record used.
_UnusedType = airtable.Record[Dict[str, Any]]


if __name__ == '__main__':
    unittest.main()
