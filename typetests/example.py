from typing import TypedDict

import airtable


# Strongly typed fields.
class MyFields(TypedDict):
    name: str
    score: float


# Example from the README.
at = airtable.Airtable('BASE_ID', 'API_KEY')
records = at.get('TABLE_NAME')

# Get the fields of a record.
record = at.get('TABLE_NAME', 'recmlj')
record['id']
record['fields']

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
