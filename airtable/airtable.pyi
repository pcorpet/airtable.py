import typing
from typing import Any, Dict, Generic, Iterable, Iterator, List, Literal, Mapping, Optional, TypedDict, Union, overload

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


_RecordType = typing.TypeVar('_RecordType', bound=Mapping[str, Any])


# TODO(pcorpet): Switch to use TypedDict, when https://github.com/python/mypy/issues/3863 is
# implemented.
class _AirtableRecord(Generic[_RecordType]):
    @overload
    def __getitem__(self, key: Literal['id']) -> str:
        ...

    @overload
    def __getitem__(self, key: Literal['createdTime']) -> str:
        ...

    @overload
    def __getitem__(self, key: Literal['fields']) -> _RecordType:
        ...


_DefaultRecordType = _AirtableRecord[_RecordType]


class _DeletedRecord(TypedDict):
    deleted: bool
    id: str


class AirtableError(Exception):

    type: str
    message: str

    def __init__(self, error_type: str, message: str) -> None:
        ...


class Table(Generic[_RecordType]):
    @overload
    def __init__(
            self, base_id: str, table_name: str, api_key: str,  dict_class: type = ...) -> None:
        ...

    @overload
    def __init__(
            self, base_id: Airtable, table_name: str, api_key: None = ...,
            dict_class: type = ...) -> None:
        ...

    def iterate(
            self,
            batch_size: int = 0,
            filter_by_formula: Optional[str] = None,
            view: Optional[str] = None,
            max_records: int = 0,
            fields: Iterable[str] = ...) -> Iterator[_AirtableRecord[_RecordType]]:
        ...

    @overload
    def get(
            self,
            record_id: None = None,
            limit: int = 0,
            offset: Optional[int] = None,
            filter_by_formula: Optional[str] = None,
            view: Optional[str] = None,
            max_records: int = 0,
            fields: Iterable[str] = ...) -> Dict[str, List[_AirtableRecord[_RecordType]]]:
        ...

    @overload
    def get(
            self,
            record_id: str,
            limit: Literal[0] = ...,
            offset: None = None,
            filter_by_formula: None = None,
            view: None = None,
            max_records: Literal[0] = 0,
            fields: Iterable[str] = ...) \
            -> _AirtableRecord[_RecordType]:
        ...

    def create(self, data: Mapping[str, Any]) -> _AirtableRecord[_RecordType]:
        ...

    def update(
            self, record_id: str,
            data: Mapping[str, Any]) -> _AirtableRecord[_RecordType]:
        ...

    def update_all(
            self, record_id: str,
            data: Mapping[str, Any]) -> _AirtableRecord[_RecordType]:
        ...

    def delete(self, record_id: str) -> _DeletedRecord:
        ...


class Airtable(object):
    airtable_url: str = ...
    base_url: str = ...
    headers: Mapping[str, str] = ...

    def __init__(
            self, base_id: str, api_key: str, dict_class: type = ...) -> None:
        ...

    def iterate(
            self,
            table_name: str,
            batch_size: int = 0,
            filter_by_formula: Optional[str] = None,
            view: Optional[str] = None,
            max_records: int = 0,
            fields: Iterable[str] = ...) -> Iterator[_DefaultRecordType]:
        ...

    @overload
    def get(
            self,
            table_name: str,
            record_id: None = None,
            limit: int = 0,
            offset: Optional[int] = None,
            filter_by_formula: Optional[str] = None,
            view: Optional[str] = None,
            max_records: int = 0,
            fields: Iterable[str] = ...) -> Dict[str, List[_DefaultRecordType]]:
     ...

    @overload
    def get(
            self,
            table_name: str,
            record_id: str,
            limit: Literal[0] = 0,
            offset: None = None,
            filter_by_formula: None = None,
            view: None = None,
            max_records: Literal[0] = 0,
            fields: Iterable[str] = ...) \
            -> _DefaultRecordType:
        ...

    def create(self, table_name: str, data: _RecordType) -> _AirtableRecord[_RecordType]:
        ...

    def update(self, table_name: str, record_id: str, data: _RecordType) \
            -> _AirtableRecord[_RecordType]:
        ...

    def update_all(self, table_name: str, record_id: str, data: _RecordType) \
            -> _AirtableRecord[_RecordType]:
        ...

    def delete(self, table_name: str, record_id: str) -> _DefaultRecordType:
        ...

    def table(self, table_name: str) -> Table[_RecordType]:
        ...
