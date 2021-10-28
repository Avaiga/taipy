import typing as t
import re

__expr_var_name_index: t.Dict[str, int] = {}
_RE_NOT_IN_VAR_NAME = r"[^A-Za-z0-9]+"


def _get_expr_var_name(expr: str) -> str:
    var_name = re.sub(_RE_NOT_IN_VAR_NAME, "_", expr)
    index = 0
    if var_name in __expr_var_name_index.keys():
        index = __expr_var_name_index[var_name]
    __expr_var_name_index[var_name] = index + 1
    return f"tp_{var_name}_{index}"
