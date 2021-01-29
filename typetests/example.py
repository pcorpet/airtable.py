from typing import Any, Mapping, TypedDict

import airtable


# Strongly typed fields.
class NameFields(TypedDict):
    name: str


class MyFields(NameFields):
    score: float


# Example from the README.
at = airtable.Airtable('BASE_ID', 'API_KEY')
records = at.get('TABLE_NAME')

# Get the fields of a record.
record = at.get('TABLE_NAME', 'recmlj')
record_id: str = record['id']
record_fields: Mapping[str, Any] = record['fields']
record_id = record.get('id')
record.get('fields', {}).get('a')

# Create a record.
created = at.create('TABLE_NAME', {'a': 3})
created['fields']['b']

# Iterate.
first = next(at.iterate('TABLE_NAME'))

# Delete
deleted = at.delete('TABLE_NAME', 'rec12341243')

# Create a strongly typed record.
data: MyFields = {'name': 'a', 'score': 3}
typed_created = at.create('TABLE_NAME', data)
typed_created['fields']['score']

# Table access, strongly typed.
scores: airtable.Table[MyFields] = at.table('scores')
name: str = scores.get('rec12341243')['fields']['name']
score: float = scores.get('rec12341243')['fields']['score']
scores.update('rec12341243', {'score': 4})

# Ensure covariance.
named_record: airtable.Record[NameFields] = scores.get('rec12341243')
