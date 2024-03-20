import os
from datetime import datetime
import pandas as pd


directories = ['data/cleaned/indeed','data/cleaned/yc']
date = str(datetime.now().strftime("%Y_%m_%d"))
all_jobs = pd.DataFrame()

def get_paths(directories):
    '''
    Generator function to yield all the paths of the files in the directories.'''
    for directory in directories:
        for filename in os.listdir(directory):
            yield os.path.join(directory, filename)


def get_data(path):
    '''
    Function to yield the data from the files.'''
    df = pd.read_csv(path)
    return df


def save_aggregated_data(data, path):
    data.to_csv(path, index=False)


if __name__ == '__main__':
    for path in get_paths(directories):
        data = get_data(path)
        all_jobs = pd.concat([all_jobs,data])
    all_jobs=all_jobs.drop_duplicates()
    all_jobs.to_csv(f'data/processed/{date}.csv', index=False)