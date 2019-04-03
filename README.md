# Airtable.py: Python API wrapper for Airtable

Python interface to the Airtable's REST API - https://airtable.com - [![Build Status](https://travis-ci.org/josephbestjames/airtable.py.svg?branch=master)](https://travis-ci.org/josephbestjames/airtable.py)

For javascript enthusiasts: https://github.com/Airtable/airtable.js

## Installation

Airtable Python uses [Requests.py](http://docs.python-requests.org/): make sure you have it installed by running

    $ pip install requests

## Getting started

Once you have created [a new base](https://support.airtable.com/hc/en-us/articles/202576419-Introduction-to-Airtable-bases) and a new table through the Web interface, you're ready to start using Airtable Python.

```python
from airtable import airtable
at = airtable.Airtable('BASE_ID', 'API_KEY')
at.get('TABLE_NAME')
```

Here's an example of response from the Restaurant's example base
```python
{u'records': [
  {u'fields': {u'Diet': u'Kosher or Halal',
    u'Friendly Restaurants': [u'recr0ITqq9C1I92FL', u'recGeAJLw0ZkbwdXZ'],
    u'Icon': [{u'filename': u'no-pig.jpg',
      u'id': u'attzKGOBbjndOx0FU',
      u'size': 34006,
      u'thumbnails': {u'large': {u'height': 202,
        u'url': u'https://dl.airtable.com/trmtq3BaRoa0sWnyffWZ_large_no-pig.jpg',
        u'width': 256},
       u'small': {u'height': 36,
        u'url': u'https://dl.airtable.com/yzuRv5CyRs2PVH4fDvCe_small_no-pig.jpg',
        u'width': 46}},
      u'type': u'image/jpeg',
      u'url': u'https://dl.airtable.com/DyGOjAASze6AIkQxFpDv_no-pig.jpg'}],
    u'People': [u'Annie', u'Maryam']},
   u'id': u'rec5sD6mBBd0SaXof'},
   ...
```

## API Reference

The available methods closely mimick the [REST API](https://airtable.com/api):

### Get
Given a table name, fetched one or multiple records.
```python
at.get(table_name, table_name, record_id=None, limit=0, offset=None,
       filter_by_formula=None, view=None, max_records=0, fields=[])
```
where
```
table_name (required) is a string representing the table name
record_id (optional) is a string, which fetches a specific item by id. If not specified, all items are fetched
limit (optional) is an integer, and it can only be specified if record_id is not present, and limits the number of items fetched (see pageSize in the AirTable documentation)
offset is a string representing the record id from which we start the offset
filter_by_formula (optional) is a string to filter the retrieving records (see filterByFormula in the AirTable documentation)
max_records (optional) is the total number of records that will be returned (see maxRecords in the AirTable documentation)
fields (optional) is a list of strings with the field names to be returned
```



### Iterate

Given a table name, fetched all records.

```python
at.iterate(table_name, table_name, limit=0, offset=None,
       filter_by_formula=None, view=None, max_records=0, fields=[])
```

where

```
table_name (required) is a string representing the table name
limit (optional) is an integer, and it can only be specified if record_id is not present, and limits the number of items fetched (see pageSize in the AirTable documentation)
offset is a string representing the record id from which we start the offset
filter_by_formula (optional) is a string to filter the retrieving records (see filterByFormula in the AirTable documentation)
max_records (optional) is the total number of records that will be returned (see maxRecords in the AirTable documentation)
fields (optional) is a list of strings with the field names to be returned
```

**Note**: this returns a generator instead, which you can use to loop each record:

```python
# example with similar results of at.get
result = { "records": [] }
for r in self.at.iterate(self.table, fields=fields):
    result["records"].append(r)
```

### Create

Creates a new entry in a table, and returns the newly created entry with its new ID.
```python
at.create(table_name, data)
```
where
```
table_name (required) is a string representing the table name
data (required) is a dictionary containing the fields and the resepective values
```

### Update
Updates *some* fields in a specific entry in the table. Fields which are not explicitely included will not get updated
```python
at.update(table_name, record_id, data)
```
where
```
table_name (required) is a string representing the table name
record_id (required) is a string representing the item to update
data (required) is a dictionary containing the fields (and the resepective values) to be updated
```

### Update All
Like the previous method, but updates all fields, clearing the ones that are not included in the request.
```python
at.update_all(table_name, record_id, data)
```

### Delete
Delete a specific record from the table
```python
at.delete(table_name, record_id)
```
where
```
table_name (required) is a string representing the table name
record_id (required) is a string representing the item to update
```
