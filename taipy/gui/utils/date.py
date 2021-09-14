from datetime import datetime
from dateutil import parser


def dateToISO(date: datetime) -> str:
    # return date.isoformat() + 'Z'
    return date.astimezone().isoformat()


def ISOToDate(date_str: str) -> datetime:
    # return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    # return datetime.fromisoformat(date_str)
    return parser.parse(date_str)
