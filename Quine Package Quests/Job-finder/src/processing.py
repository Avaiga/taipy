import os
import pandas as pd
from datetime import datetime

DIRECTORIES = ["data/raw/indeed/", "data/raw/yc"]
required_columns = [
    "title",
    "company",
    "salary",
    "location",
    "link",
    "date",
    "query",
    "source",
]
RAW = "raw"
AGGREGATE_PATH = "data/aggregate/aggregate.csv"
CLEANED = "cleaned"

dataframes = []

# TODO: add aggregation of jobs - return a single csv file for all


def get_paths(directories):
    """
    Generator function to yield all the paths of the files in the directories."""
    for directory in directories:
        for filename in os.listdir(directory):
            yield os.path.join(directory, filename)


def get_data(path):
    """
    Function to yield the data from the files."""
    df = pd.read_csv(path)
    return df


def process_link(link, prefix):
    if not str(link).startswith('https'):
        return prefix + link
    return link

def process_data(data, source):
    data = data.drop_duplicates()
    data = data.dropna(axis=0, subset=["title", "link"])

    data["source"] = source
    if source == "indeed":
        data["link"] = data["link"].apply(lambda x :process_link(x, 'https://in.indeed.com'))
    elif source == "yc":
        data["link"] = data["link"].apply(
            lambda x: process_link(x, 'https://ycombinator.com')
        )

    # check for required columns
    columns = set(data.columns)
    if columns != set(required_columns):
        absent_columns = set(required_columns) - columns
        if "salary" in absent_columns:
            data["salary"] = "Not Specified"

    if "duration" in columns:
        data = data.drop(columns=["duration"])

    # re order columns - same format for aggregation
    data = data[required_columns]
    # really necessary, but try alternative options
    data["salary"] = data["salary"].fillna("Not Specified")

    return data


# TODO : parse dates, remove jobs older than 20 days or so
# TODO : if all required columns not present, init with empty values


def process_and_save_data():
    for path in get_paths(DIRECTORIES):
        data = get_data(path)
        if data is not None:
            source = os.path.basename(os.path.dirname(path))
            data = process_data(data, source)
            path = str(path).replace(RAW, CLEANED)
            dataframes.append(data)
    # TODO : add a last date run check to prevent duplication of records
    if dataframes:
        aggregated_data = pd.concat(dataframes, ignore_index=True)
        if os.path.exists(AGGREGATE_PATH):
            previous_aggregate = pd.read_csv(AGGREGATE_PATH)
            aggregated_data = pd.concat(
                [aggregated_data, previous_aggregate], ignore_index=True
            )
        print(len(aggregated_data))
        aggregated_data = aggregated_data.reindex(index=aggregated_data.index[::-1])
        aggregated_data.to_csv(AGGREGATE_PATH, index=False)
    else:
        print("No dataframes to aggregate")


if __name__ == "__main__":
    process_and_save_data()
