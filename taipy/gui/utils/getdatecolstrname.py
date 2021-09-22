import pandas as pd

def get_date_col_str_name(df: pd.DataFrame, col: str):
    sufix = "_str"
    while col + sufix in df.columns:
        sufix =+ "_"
    return col + sufix