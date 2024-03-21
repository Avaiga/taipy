import logging
from taipy.gui import builder as tgb
from taipy.gui import navigate
import pandas as pd



logging.basicConfig(level=logging.INFO)

df = pd.read_csv("data/aggregate/aggregate.csv")

filtered_df = df
locations = list(df["location"].unique())
queries = [
    "python developer",
    "data analyst",
    "machine learning engineer",
    "software engineer",
    "backend developer",
    "devops engineer",
    "automation engineer",
    "network engineer",
    "vuejs developer",
    "react developer",
    "nodejs developer",
    "frontend developer",
    "full stack developer",
    "ui developer",
    "web application developer",
    "javascript engineer",
    "mobile app developer",
]
sources = ["indeed", "yc"]
links = {}
chunk_index = 0
selected_locations, selected_queries, selected_sources = [], [], []
filter_options=['location','source','title']
selected_options =''


def choose_filter_option(state):
    if state.selected_option=='location':
        tgb.selector()


with tgb.Page() as search_page:
    tgb.text('Filter by', class_name='h3')
    tgb.html('br')
    with tgb.layout('1 1 1'):
        with tgb.part('card'):
            tgb.text('Job Title', class_name='h4')
            tgb.html('br')
            tgb.selector(value='{selected_queries}', lov=queries, multiple=False, dropdown=True)
        with tgb.part('card'):
            tgb.text('Location', class_name='h4')
            tgb.html('br')
            tgb.selector(value='{selected_locations}', lov=locations, multiple=False, dropdown=True)
        with tgb.part('card'):
            tgb.text('Job Source')
            tgb.html('br')
            tgb.selector(value='{selected_sources}', lov=sources, multiple=False, dropdown=True)
