import os

def get_mapbox_token():
    mapbox_token = os.environ.get('MAPBOX_TOKEN')
    if mapbox_token is None:
        raise ValueError("Mapbox Access token is not set as an environment variable")
    return mapbox_token