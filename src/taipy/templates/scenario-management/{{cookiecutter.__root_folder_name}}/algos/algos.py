def clean_data(df, replacement_type):
    df = df.fillna(replacement_type)
    return df
