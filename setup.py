from setuptools import setup
setup(
    name='airtable',
    version='0.4.1',
    packages=['airtable'],
    package_data={'airtable': ['py.typed', '*.pyi']},
    install_requires=['requests>=2.20.0', 'six'],
    description='Python client library for AirTable',
    author='Joseph Best-James, Nicolo Canali De Rossi, Pascal Corpet',
    url='https://github.com/josephbestjames/airtable.py',
    keywords=['airtable', 'api'],
    license='The MIT License (MIT)',
)
