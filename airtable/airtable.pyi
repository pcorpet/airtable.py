import typing
from typing import Any, TypedDict

API_URL: str
API_VERSION: str

class IsNotInteger(Exception):
    ...

class IsNotString(Exception):
    ...

def check_integer(n: Any) -> bool:
    ...

def check_string(s: Any) -> bool:
    ...

def create_payload(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    ...


_DefaultRecord = typing.Dict[str, typing.Any]
RecordType = typing.TypeVar('RecordType', bound=_DefaultRecord)

class _Record(TypedDict, Generic[RecordType]):
    id: str
    createdTime: str
    fields: RecordType


class _DeletedRecord(TypedDict):
    deleted: bool
    id: str


class AirtableTable(Generic[RecordType]):
    def __init__(self, base_id: str, api_key: str) -> None:
        ...

    def iterate(
            self,
            batch_size: int = 0,
            filter_by_formula: typing.Optional[str] = None,
            view: typing.Optional[str] = None) -> typing.Iterator[_Record[RecordType]]:
        ...

    @typing.overload
    def get(
            self,
            record_id: None = None,
            limit: int = 0,
            offset: typing.Optional[int] = None,
            filter_by_formula: typing.Optional[str] = None,
            view: typing.Optional[str] = None) \
            -> typing.Dict[str, typing.List[_Record[RecordType]]]:
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
            -> _Record[RecordType]:
        ...

    def create(self, data: typing.Dict[str, typing.Any]) -> _Record[RecordType]:
        ...

    def update(self, record_id: str, data: RecordType) -> _Record[RecordType]:
        ...

    def update_all(self, record_id: str, data: RecordType) -> _Record[RecordType]:
        ...

    def delete(self, table_name: str, record_id: str) -> _DeletedRecord:
        ...


class Airtable(object):
    airtable_url: str = ...
    base_url: str = ...
    headers: Dict[str, str] = ...

    def __init__(self, base_id: str, api_key: str) -> None:
        ...

    def iterate(
            self,
            table_name: str,
            batch_size: int = 0,
            filter_by_formula: Optional[str] = None,
            view: Optional[str] = None) -> Iterator[_Record]:
        ...

    @overload
    def get(
            self,
            table_name: str,
            record_id: None = None,
            limit: int = 0,
            offset: Optional[int] = None,
            filter_by_formula: Optional[str] = None,
            view: Optional[str] = None) \
            -> Dict[str, List[_Record]]:
     ...

    @overload
    def get(
            self,
            table_name: str,
            record_id: str,
            limit: int = 0,
            offset: Optional[int] = None,
            filter_by_formula: Optional[str] = None,
            view: Optional[str] = None) \
            -> _Record[_DefaultRecord]:
        ...

    def create(self, table_name: str, data: _DefaultRecord) -> _Record[_DefaultRecord]:
        ...

    def update(self, table_name: str, record_id: str, data: _DefaultRecord) \
            -> _Record[_DefaultRecord]:
        ...

    def update_all(self, table_name: str, record_id: str, data: _DefaultRecord) \
            -> _Record[_DefaultRecord]:
        ...

    def delete(self, table_name: str, record_id: str) -> _DeletedRecord:
        ...

    def table(self, table_name: str) -> AirtableTable[RecordType]:
        ...
