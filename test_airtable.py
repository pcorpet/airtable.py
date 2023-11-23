from typing import Any, Dict
import unittest
import json

import requests_mock
import httpretty
import airtable
import re

FAKE_TABLE_NAME = 'TableName'
FAKE_BASE_ID = 'app12345'
FAKE_API_KEY = 'fake_api_key'


class TestAirtable(unittest.TestCase):
    def setUp(self):
        self.base_id = FAKE_BASE_ID
        self.api_key = FAKE_API_KEY
        self.airtable = airtable.Airtable(self.base_id, self.api_key)

    def get(self, *args, **kwargs):  # pylint: disable=invalid-name
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

    @httpretty.activate
    def test_retries(self):
        httpretty.register_uri(
            httpretty.GET,
            re.compile(r'https://.*'),
            responses=[
                httpretty.Response(
                    body='{}',
                    status=429,
                ),
                httpretty.Response(
                    body='{}',
                    status=500,
                ),
                 httpretty.Response(
                    body=json.dumps({
                        'records': [
                            {
                                'id': 'reccA6yaHKzw5Zlp0',
                                'fields': {
                                    'Name': 'John',
                                    'Number': '(987) 654-3210'
                                }
                            }
                        ],
                        'offset': 'reccg3Kke0QvTDW0H'
                    }),
                    status=200,
                ),
            ]
        )
        
        res = self.get()
        self.assertEqual(3, len(httpretty.latest_requests()))
        self.assertEqual(len(res['records']), 1)
        self.assertEqual(res['offset'], 'reccg3Kke0QvTDW0H')

    @requests_mock.mock()
    def test_get_all(self, mock_requests):
        mock_requests.get('https://api.airtable.com/v0/app12345/TableName', json={
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
        })
        res = self.get()
        self.assertEqual(len(res['records']), 2)
        self.assertEqual(res['offset'], 'reccg3Kke0QvTDW0H')

    @requests_mock.mock()
    def test_order_of_fields_is_preserved(self, mock_requests):
        # Set the text content of the response to a JSON string so we can test
        # how it gets deserialized
        mock_requests.get('https://api.airtable.com/v0/app12345/TableName', text='''{
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
        }''')

        response = self.airtable.get(FAKE_TABLE_NAME)
        self.assertEqual(list(response['records'][0]['fields'].keys()), list(u'abcdefghijklm'))
        self.assertEqual(list(response['records'][1]['fields'].keys()), list(u'nopqrstuvwxyz'))

    @requests_mock.mock()
    def test_get_by_id(self, mock_requests):
        fake_id = 'reccA6yaHKzw5Zlp0'
        mock_requests.get('https://api.airtable.com/v0/app12345/TableName/reccA6yaHKzw5Zlp0', json={
            'id': 'reccA6yaHKzw5Zlp0',
            'fields': {
                'Name': 'John',
                'Number': '(987) 654-3210'
            }
        })
        response = self.get(fake_id)
        self.assertEqual(response['id'], fake_id)

    @requests_mock.mock()
    def test_get_not_found(self, mock_requests):
        mock_requests.get(
            'https://api.airtable.com/v0/app12345/TableName/123', status_code=404,
            json={
                'error': {
                    'type': 'TABLE_NOT_FOUND',
                    'message': 'Could not find table %s in application %s' % (
                        FAKE_TABLE_NAME, FAKE_BASE_ID),
                },
            })
        with self.assertRaises(airtable.AirtableError) as error:
            self.get('123')
        self.assertEqual('TABLE_NOT_FOUND', error.exception.type)

    @requests_mock.mock()
    def test_get_view(self, mock_requests):
        mock_requests.get(
            'https://api.airtable.com/v0/app12345/TableName?view=My+view',
            request_headers={'Authorization': 'Bearer fake_api_key'},
            json={'records': []})

        self.get(view='My view')
        self.assertEqual(1, mock_requests.called)

    @requests_mock.mock()
    def test_get_only_one_field(self, mock_requests):
        mock_requests.get(
            'https://api.airtable.com/v0/app12345/TableName?fields=Name&fields=Name',
            request_headers={'Authorization': 'Bearer fake_api_key'},
            json={'records': []})

        self.get(fields=['Name'])
        self.assertEqual(1, mock_requests.called)

    @requests_mock.mock()
    def test_get_filter_by_formula(self, mock_requests):
        mock_requests.get(
            "https://api.airtable.com/v0/app12345/TableName?filterByFormula=%7Btitle%7D+%3D+%27%27",
            request_headers={'Authorization': 'Bearer fake_api_key'},
            json={'records': []})

        self.get(filter_by_formula="{title} = ''")
        self.assertEqual(1, mock_requests.called)

    def test_invalid_get(self):
        with self.assertRaises(airtable.IsNotString):
            self.get(123)
            self.get(offset=123)
        with self.assertRaises(airtable.IsNotInteger):
            self.get(limit='1')

    @requests_mock.mock()
    def test_delete(self, mock_requests):
        mock_requests.delete(
            'https://api.airtable.com/v0/app12345/TableName/1234',
            request_headers={'Authorization': 'Bearer fake_api_key'},
            json={
                'deleted': True,
                'id': '1234'
            })
        response = self.delete('1234')
        self.assertTrue(response['deleted'])
        self.assertEqual(response['id'], '1234')

    def test_invalid_delete(self):
        with self.assertRaises(airtable.IsNotString):
            self.delete(123)

    @requests_mock.mock()
    def test_iterate(self, mock_requests):
        mock_requests.get(
            'https://api.airtable.com/v0/app12345/TableName',
            json={
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
            })
        mock_requests.get(
            'https://api.airtable.com/v0/app12345/TableName?offset=reccg3Kke0QvTDW0H',
            json={
                'records': [
                    {
                        'id': 'reccA23fSERw5Zlp0',
                        'fields': {
                            'Name': 'Ron',
                            'Number': '(987) 654-3210'
                        }
                    },
                ],
            })
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

    @requests_mock.mock()
    def test_typed_table(self, mock_requests):
        mock_requests.get(
            'https://api.airtable.com/v0/app12345/TableName',
            json={
                'records': [
                    {
                        'id': 'reccA23fSERw5Zlp0',
                        'fields': {
                            'Name': 3,
                            'Number': 4
                        }
                    },
                ],
            })

        table = airtable.Table[Dict[str, int]](
            self.base_id, FAKE_TABLE_NAME, api_key=FAKE_API_KEY)
        response = table.get()
        self.assertEqual(response['records'][0]['fields'], {'Name': 3, 'Number': 4})


class TestNestedModule(TestAirtable):

    def setUp(self):
        super(TestNestedModule, self).setUp()
        self.airtable = airtable.airtable.Airtable(self.base_id, self.api_key)


# This line is here only to check that Python code supports having the Record used.
_UnusedType = airtable.Record[Dict[str, Any]]


if __name__ == '__main__':
    unittest.main()
