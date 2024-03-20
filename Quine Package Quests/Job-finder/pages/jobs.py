import logging
from taipy.gui import Gui, navigate
import taipy.gui.builder as tgb
import pandas as pd

logging.basicConfig(level=logging.INFO)

df = pd.read_csv("data/aggregate/aggregate.csv")

filtered_df = df
selected_locations = list(df["location"].unique())
selected_queries = [
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
    "other",
]
selected_sources = ["indeed", "yc"]
links = {}
chunk_index = 0


def get_chunks(df, chunk_size=20):
    n_chunks = len(df) // chunk_size + 1
    for i in range(n_chunks):
        yield df.iloc[i * chunk_size : (i + 1) * chunk_size]


chunks = list(get_chunks(filtered_df))

def filter_data(state):
    print(state.selected_locations, state.selected_sources, state.selected_queries)
    state.filtered_df = state.filtered_df[
        state.filtered_df["location"].isin([state.selected_locations])
        & state.filtered_df["source"].isin([state.selected_sources])
        & state.filtered_df["query"].isin([state.selected_queries])
    ]
    state.chunk_index=0
    if state.filtered_df.empty:
        logging.warning("No filtered rows available")

    simulate_adding_more_links(state)


def navigate_to_link(state, link_url, payload=None):
    navigate(state, to=link_url, force=True)


# todo : On interacting with selector, it refreshes chunk without actually filtering, fix this


def simulate_adding_more_links(state):
    state.selected_sources = 'indeed'
    state.selected_queries = 'python developer'
    state.selected_locations = 'remote'
    state.chunks = list(get_chunks(state.filtered_df))
    if state.chunk_index < len(state.chunks):
        chunk = state.chunks[state.chunk_index]
        if not chunk.empty:
            logging.info(f"processing chunk {state.chunk_index}")
            logging.info(chunk.index[0])
            chunk.reset_index(drop=True, inplace=True)
            state.links = {"link_" + str(i): row for i, row in chunk.iterrows()}
        state.chunk_index += 1


with tgb.Page() as link_part:
    tgb.text('Find Jobs', class_name='h2')
    tgb.html('br')
    with tgb.layout("4 1 1"):
        tgb.selector(
            value="{selected_queries}",
            lov=selected_queries,
            on_change=filter_data,
            dropdown=True,
            multiple=False,
            class_name="fullwidth",
        )
        tgb.selector(
            value="{selected_locations}",
            lov=selected_locations,
            on_change=filter_data,
            dropdown=True,
            multiple=False,
            class_name="fullwidth",
        )
        tgb.selector(
            value="{selected_sources}",
            lov=selected_sources,
            on_change=filter_data,
            dropdown=True,
            multiple=False,
            class_name="fullwidth",
        )
    with tgb.layout("1 1 1 1"):
        for i in range(20):
            with tgb.part("card"):
                tgb.text("{links['link_" + str(i) + "']['title']}", class_name="h3")
                tgb.html("br")
                with tgb.layout("1 1"):
                    tgb.text(
                        "{links['link_" + str(i) + "']['company']}", class_name="h5"
                    )
                    tgb.text(
                        "{links['link_" + str(i) + "']['location']}", class_name="h5"
                    )
                tgb.button(
                    "Apply",
                    on_action=navigate_to_link,
                    id="{links['link_" + str(i) + "']['link']}",
                    class_name="plain",
                )

    tgb.button("See more jobs", on_action=simulate_adding_more_links)


def on_init(state):
    simulate_adding_more_links(state)


# * do not use the following line if running the multi page app, it is only for debugging
Gui(link_part).run(debug=True, use_reloader=True)
