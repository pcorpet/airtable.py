import typing

API_URL: str
API_VERSION: str

class IsNotInteger(Exception):
    ...

class IsNotString(Exception):
    ...

def check_integer(n: typing.Any) -> bool:
    ...

def check_string(s: typing.Any) -> bool:
    ...

def create_payload(data: typing.Dict[str, typing.Any]) \
        -> typing.Dict[str, typing.Dict[str, typing.Any]]:
    ...

_Record = typing.Dict[str, typing.Union[str, typing.Dict[str, typing.Any]]]

class Airtable(object):
    airtable_url: str = ...
    base_url: str = ...
    headers: typing.Dict[str, str] = ...

    def __init__(self, base_id: str, api_key: str) -> None:
        ...

    def iterate(
            self,
            table_name: str,
            batch_size: int = 0,
            filter_by_formula: typing.Optional[str] = None,
            view: typing.Optional[str] = None) -> typing.Iterator[_Record]:
        ...

    @typing.overload
    def get(
            self,
            table_name: str,
            record_id: None = None,
            limit: int = 0,
            offset: typing.Optional[int] = None,
            filter_by_formula: typing.Optional[str] = None,
            view: typing.Optional[str] = None) \
            -> typing.Dict[str, typing.List[_Record]]:
     ...

    @typing.overload
    def get(
            self,
            table_name: str,
            record_id: str,
            limit: int = 0,
            offset: typing.Optional[int] = None,
            filter_by_formula: typing.Optional[str] = None,
            view: typing.Optional[str] = None) \
            -> _Record:
        ...

    def create(self, table_name: str, data: typing.Dict[str, typing.Any]) -> _Record:
        ...
 
    def update(self, table_name: str, record_id: str, data: typing.Dict[str, typing.Any]) -> _Record:
        ...

    def update_all(self, table_name: str, record_id: str, data: typing.Dict[str, typing.Any]) -> _Record:
        ...

    def delete(self, table_name: str, record_id: str) -> typing.Dict[str, typing.Union[str, bool]]:
        ...
