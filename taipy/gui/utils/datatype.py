import re


def getDataType(value):
    return re.match(r"^<class '(.*?)'>", str(type(value))).group(1)
