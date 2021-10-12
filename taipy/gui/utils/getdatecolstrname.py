import pandas as pd


def get_date_col_str_name(df: pd.DataFrame, col: str):
    suffix = "_str"
    while col + suffix in df.columns:
        suffix += "_"
    return col + suffix
