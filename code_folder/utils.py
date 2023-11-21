def get_min_and_max_timestamp(df):
    min_date = df.iso_timestamp.min().date()
    max_date = df.iso_timestamp.max().date()
    return min_date, max_date