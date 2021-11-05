import re

import unidecode


def protect_name(name: str):
    # get protect name by converting unicode characters to ASCII and removing special characters
    return re.sub(r"[\W]+", "-", unidecode.unidecode(name).strip().lower().replace(" ", "_"))
