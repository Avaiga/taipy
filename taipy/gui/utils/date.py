import typing as t
import warnings
from datetime import date, datetime, time

from dateutil import parser
from pytz import utc


def _date_to_ISO(date_val: t.Union[datetime, date, time]) -> str:
    if isinstance(date_val, datetime):
        # return date.isoformat() + 'Z', if possible
        try:
            return date_val.astimezone(utc).isoformat()
        except Exception as e:
            # astimezone() fails on Windows for pre-epoch times
            # See https://bugs.python.org/issue36759
            warnings.warn(f"There is some problems with date parsing to ISO!\n{e}")
    return date_val.isoformat()


def _ISO_to_date(date_str: str) -> datetime:
    # return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    # return datetime.fromisoformat(date_str)
    return parser.parse(date_str)
