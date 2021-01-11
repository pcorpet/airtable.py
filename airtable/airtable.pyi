import typing
from typing import Any, Dict, Iterable, Iterator, List, Optional, TypedDict, overload

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


class _Record(TypedDict):
    id: str
    createdTime: str
    fields: Dict[str, Any]


class _DeletedRecord(TypedDict):
    deleted: bool
    id: str


# TODO(cyrille): Add Generic[RecordType] for more information on what's in a record.
class Airtable(object):
    airtable_url: str = ...
    base_url: str = ...
    headers: Dict[str, str] = ...

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
            fields: Iterable[str] = ...) -> Iterator[_Record]:
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
            fields: Iterable[str] = ...) -> Dict[str, List[_Record]]:
     ...

    @overload
    def get(
            self,
            table_name: str,
            record_id: str,
            limit: int = 0,
            offset: Optional[int] = None,
            filter_by_formula: Optional[str] = None,
            view: Optional[str] = None,
            max_records: int = 0,
            fields: Iterable[str] = ...) \
            -> _Record:
        ...

    def create(self, table_name: str, data: Dict[str, Any]) -> _Record:
        ...

    def update(self, table_name: str, record_id: str, data: Dict[str, Any]) -> _Record:
        ...

    def update_all(self, table_name: str, record_id: str, data: Dict[str, Any]) -> _Record:
        ...

    def delete(self, table_name: str, record_id: str) -> _DeletedRecord:
        ...
