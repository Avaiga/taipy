import re


def _get_data_type(value):
    return re.match(r"^<class '(.*?)'>", str(type(value))).group(1)
