import typing as t


def _get_date_col_str_name(columns: t.List[str], col: str) -> str:
    suffix = "_str"
    while col + suffix in columns:
        suffix += "_"
    return col + suffix
