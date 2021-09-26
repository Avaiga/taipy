from datetime import datetime
from pytz import utc

from dateutil import parser


def dateToISO(date: datetime) -> str:
    # return date.isoformat() + 'Z', if possible
    try:
        return date.astimezone(utc).isoformat()
    except Exception:
        # astimezone() fails on Windows for pre-epoch times
        # See https://bugs.python.org/issue36759
        print("There is some problems with date parsing to ISO!")
        return date.isoformat()


def ISOToDate(date_str: str) -> datetime:
    # return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    # return datetime.fromisoformat(date_str)
    return parser.parse(date_str)
