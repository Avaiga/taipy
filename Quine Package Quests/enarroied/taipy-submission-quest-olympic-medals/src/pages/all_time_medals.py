import pandas as pd
import plotly.express as px
import taipy.gui.builder as tgb

###########################################################
###                    Load Datasets                    ###
###########################################################
df_olympic_cities = pd.read_csv("./data/olympic_cities.csv")
df_olympic_medals = pd.read_csv("./data/olympic_medals.csv")

###########################################################
###             Ceate transformed DataFrames            ###
###########################################################

# Small DataFrame to display as summary table
df_olympic_cities_simplified = df_olympic_cities[
    [
        "Olympiad",
        "Olympic_year",
        "Olympic_season",
        "total_medals",
        "total_medals_gold",
        "total_medals_silver",
        "total_medals_bronze",
        "number_committees",
        "number_disciplines",
        "number_events",
        "Country",
        "Continent",
    ]
]

# Define a custom sorting order for 'Medal_type'
medal_order = {"Bronze": 0, "Silver": 1, "Gold": 2}

df_medals_by_olympiad = (
    df_olympic_medals.groupby(
        ["Olympiad", "Olympic_year", "Medal_type", "Olympic_season"]
    )
    .size()
    .reset_index(name="Medal_count")
)

# Sort the DataFrame first by 'Olympic_year' and then by 'Medal_type' using the custom sorting order
df_medals_by_olympiad["Medal_type_code"] = df_medals_by_olympiad["Medal_type"].map(
    medal_order
)
df_medals_by_olympiad = df_medals_by_olympiad.sort_values(
    by=["Olympic_year", "Medal_type_code"]
)

# Reset index without creating a new column
df_medals_by_olympiad.reset_index(drop=True, inplace=True)


###########################################################
###                      Functions                      ###
###########################################################
def create_bar_medals(df_medals_by_olympiad, season):
    """Creates a plotly bar chart with total olympic medals (broken by medal color).
        The dataframe is previously filtered by season (summer / winter).

    Args:
        df_medals_by_olympiad (pd.DataFrame): data with all the olympic medals.
        season (str): ""All", "winter" or "summer".

    Returns:
       px.bar: A plotly bar chart to display in the Taipy app
    """
    # Define colors for each medal type
    medal_colors = {"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"}

    if season != "All":
        df_medals_season = df_medals_by_olympiad[
            df_medals_by_olympiad["Olympic_season"] == season
        ].reset_index(drop=True)
    else:
        df_medals_season = df_medals_by_olympiad
    # Create a stacked bar chart
    fig = px.bar(
        df_medals_season,
        x="Olympiad",
        y="Medal_count",
        color="Medal_type",
        color_discrete_map=medal_colors,  # Assign colors to medal types
        title="Medal Count by Olympiad and Medal Type",
        labels={"Medal_count": "Medal Count", "Olympiad": "Olympiad"},
        category_orders={"Olympiad": df_medals_season["Olympiad"].unique()},
    )
    if season != "winter":
        stockholm_annotation_y = 400  # Stockholm 1956 there are 18 medals total, but 400 will weep box out of othe chart elements
        stockholm_annotation_x = (
            df_medals_season[df_medals_season["Olympiad"] == "Stockholm 1956"].index[0]
            / 3
        ) + 1  # Divide by 3 because 3 types of medals

        fig.add_annotation(
            x=stockholm_annotation_x,
            y=stockholm_annotation_y,
            text=str("Stockholm 1956: only equestrian games"),
            showarrow=True,
            arrowhead=1,
            arrowcolor="#FF0066",
            arrowwidth=1,
            arrowsize=1,
            ax=0,
            ay=-50,
            font=dict(color="black", size=8),
            align="center",
            bordercolor="#c7c7c7",
            borderwidth=2,
            borderpad=4,
            bgcolor=" #B0E0E6",
            opacity=0.8,
        )
    return fig


def create_bar_by_committee(df_medals, olympiad="All"):
    """Creates a plotly bar chart with total olympic medals (medal colorS by each other).
        The dataframe is previously filtered by season (summer / winter).

    Args:
        df_medals (pd.DataFrame): data with all the olympic medals.
        olympiad (str): ""All", or name of the Olympiad.

    Returns:
       px.bar: A plotly bar chart to display in the Taipy app
    """
    df_medals_by_committee = df_medals.copy()

    if olympiad != "All":
        df_medals_by_committee = df_medals_by_committee[
            df_medals_by_committee["Olympiad"] == olympiad
        ]

    # Define medal colors
    medal_colors = {"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"}

    # Aggregating data to get count of medals by Medal_type for each Committee
    df_aggregated = (
        df_medals_by_committee.groupby(["Committee", "Medal_type"])
        .size()
        .unstack(fill_value=0)
    )

    # Sort DataFrame by count of gold and silver medals
    df_aggregated = df_aggregated.sort_values(by=["Gold", "Silver"], ascending=False)

    # Plotly bar chart
    fig = px.bar(
        df_aggregated,
        x=df_aggregated.index,
        y=["Gold", "Silver", "Bronze"],
        barmode="group",
        orientation="v",
        color_discrete_map=medal_colors,
        labels={"value": "Count", "variable": "Medal Type"},
        title="Count of Gold, Silver, Bronze Medals by Committee",
    )
    fig.update_layout(xaxis={"title": "Committee"}, yaxis={"title": "Count"})
    return fig


def plot_olympic_medals_by_country(df_olympic_cities, season, medal_type):
    """
    Plot a choropleth map of Olympic medals by country for a specified season and medal type.

    Args:
        df_olympic_medals (pandas.DataFrame): DataFrame containing Olympic medals data.
        season (str): The season for which to plot the medals. Should be either "winter" or "summer".
        medal_type (str): The type of medal to count. Should be one of "All", "Gold", "Silver", or "Bronze".

    Returns:
        None
    """
    if medal_type == "All":
        medal_column = "total_medals"
    elif medal_type == "Gold":
        medal_column = "total_medals_gold"
    elif medal_type == "Silver":
        medal_column = "total_medals_silver"
    elif medal_type == "Bronze":
        medal_column = "total_medals_bronze"
    else:
        raise ValueError(
            "Invalid medal_type. Should be one of 'All', 'Gold', 'Silver', or 'Bronze'."
        )

    if season != "All":
        df_olympic_cities = df_olympic_cities[
            df_olympic_cities["Olympic_season"] == season
        ]

    country_counts = (
        df_olympic_cities.groupby(["Country", "ISO_code_mapping"])[medal_column]
        .sum()
        .reset_index(name="Number of Medals")
    )

    fig = px.choropleth(
        country_counts,
        locations="ISO_code_mapping",
        color="Number of Medals",
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"{medal_type.capitalize()} Olympic Medals awarded by Host Country ({season.capitalize()})",
        projection="natural earth",
    )

    fig.update_geos(
        showcountries=True,
        showland=True,
        landcolor="lightgray",
        countrycolor="white",
    )

    return fig


def create_sunburnst_medals(df_olympic_medals, selected_olympiad_for_sunburst):
    gender_category_colors = {
        "Men": "#6baed6",  # Light blue
        "Women": "#fb6a4a",  # Light red
        "Open": "#74c476",  # Light green
        "Mixed": "#9e9ac8",  # Light purple
    }
    if selected_olympiad_for_sunburst != "All":
        df_olympic_medals = df_olympic_medals[
            df_olympic_medals["Olympiad"] == selected_olympiad_for_sunburst
        ]
    fig = px.sunburst(
        df_olympic_medals,
        path=["Gender", "Discipline", "Event"],
        color="Gender",
        color_discrete_map=gender_category_colors,
        title=f"Total Medals by Gender, Discipline, and Event - {selected_olympiad_for_sunburst}",
    )
    return fig


###########################################################
###                  Displayed objects                  ###
###########################################################
bar_medals = create_bar_medals(df_medals_by_olympiad, "All")
bar_medals_by_committee = create_bar_by_committee(df_olympic_medals, "All")
map_medals = plot_olympic_medals_by_country(
    df_olympic_cities, season="All", medal_type="All"
)
sunburnst_medals = create_sunburnst_medals(
    df_olympic_medals, selected_olympiad_for_sunburst="All"
)

###########################################################
###         Initial variables and selector lists        ###
###########################################################

list_seasons = ["All", "summer", "winter"]
list_olympiads = [
    "All",
    "Athina 1896",
    "Paris 1900",
    "St. Louis 1904",
    "London 1908",
    "Stockholm 1912",
    "Antwerpen 1920",
    "Paris 1924",
    "Amsterdam 1928",
    "Los Angeles 1932",
    "Berlin 1936",
    "London 1948",
    "Helsinki 1952",
    "Stockholm 1956",
    "Melbourne 1956",
    "Roma 1960",
    "Tokyo 1964",
    "Ciudad de México 1968",
    "München 1972",
    "Montréal 1976",
    "Moskva 1980",
    "Los Angeles 1984",
    "Seoul 1988",
    "Barcelona 1992",
    "Atlanta 1996",
    "Sydney 2000",
    "Athina 2004",
    "Beijing 2008",
    "London 2012",
    "Rio de Janeiro 2016",
    "Tokyo 2020",
    "Chamonix 1924",
    "Sankt Moritz 1928",
    "Lake Placid 1932",
    "Garmisch-Partenkirchen 1936",
    "Sankt Moritz 1948",
    "Oslo 1952",
    "Cortina d'Ampezzo 1956",
    "Squaw Valley 1960",
    "Innsbruck 1964",
    "Grenoble 1968",
    "Sapporo 1972",
    "Innsbruck 1976",
    "Lake Placid 1980",
    "Sarajevo 1984",
    "Calgary 1988",
    "Albertville 1992",
    "Lillehammer 1994",
    "Nagano 1998",
    "Salt Lake City 2002",
    "Torino 2006",
    "Vancouver 2010",
    "Sochi 2014",
    "PyeongChang 2018",
    "Beijing 2022",
]
list_seasons_map = ["All", "summer", "winter"]
list_medal_colors = ["All", "Gold", "Silver", "Bronze"]
season = "All"
selected_olympiad = "All"
selected_season_map = "All"
selected_medal_color = "All"
selected_olympiad_for_sunburst = "All"


###########################################################
###                  Selector Function                  ###
###########################################################
def on_selector(state):
    state.bar_medals = create_bar_medals(df_medals_by_olympiad, state.season)
    state.bar_medals_by_committee = create_bar_by_committee(
        df_olympic_medals, state.selected_olympiad
    )
    state.map_medals = plot_olympic_medals_by_country(
        df_olympic_cities,
        season=state.selected_season_map,
        medal_type=state.selected_medal_color,
    )
    state.sunburnst_medals = create_sunburnst_medals(
        df_olympic_medals, state.selected_olympiad_for_sunburst
    )


###########################################################
###                      Design Page                    ###
###########################################################


with tgb.Page() as all_time_medals:

    tgb.text("Medals awarded at all Olympic games", class_name="h2")
    tgb.text(
        "This dashboard displays aggregated data for the medals awarded across the Olympics, from Athens 1896 to Beijing 2022."
    )

    with tgb.layout("1 1 1 1"):
        with tgb.part("card card-bg"):
            tgb.text(
                "Total Gold Medals 🥇 ",
                class_name="h3",
            )
            tgb.text(
                "{int(df_olympic_medals[df_olympic_medals['Medal_type']=='Gold']['Medal_type'].count())}",
                class_name="h3",
            )

        with tgb.part("card card-bg"):
            tgb.text(
                "Total Silver Medals 🥈",
                class_name="h3",
            )
            tgb.text(
                "{int(df_olympic_medals[df_olympic_medals['Medal_type']=='Silver']['Medal_type'].count())}",
                class_name="h3",
            )

        with tgb.part("card card-bg"):
            tgb.text(
                "Total Bronze Medals 🥉",
                class_name="h3",
            )
            tgb.text(
                "{int(df_olympic_medals[df_olympic_medals['Medal_type']=='Bronze']['Medal_type'].count())}",
                class_name="h3",
            )

        with tgb.part("card card-bg"):
            tgb.text(
                "Total Medals 🏟",
                class_name="h3",
            )
            tgb.text("{int(len(df_olympic_medals))}", class_name="h3")

    # Bar chart of all medals:
    with tgb.layout("1 1"):
        with tgb.part():
            tgb.selector(
                value="{season}",
                lov=list_seasons,
                dropdown=True,
                label="Select season",
                class_name="fullwidth",
                on_change=on_selector,
            )
            tgb.chart(figure="{bar_medals}")

        with tgb.part():
            tgb.selector(
                value="{selected_olympiad}",
                lov=list_olympiads,
                dropdown=True,
                label="Select Olympiad",
                class_name="fullwidth",
                on_change=on_selector,
            )
            tgb.chart(figure="{bar_medals_by_committee}")
        with tgb.part():
            with tgb.layout("1 1"):
                with tgb.part():
                    tgb.selector(
                        value="{selected_season_map}",
                        lov=list_seasons_map,
                        dropdown=True,
                        label="Select season for map",
                        class_name="fullwidth",
                        on_change=on_selector,
                    )
                with tgb.part():
                    tgb.selector(
                        value="{selected_medal_color}",
                        lov=list_medal_colors,
                        dropdown=True,
                        label="Select medal color",
                        class_name="fullwidth",
                        on_change=on_selector,
                    )
            tgb.chart(figure="{map_medals}")
        with tgb.part():
            tgb.selector(
                value="{selected_olympiad_for_sunburst}",
                lov=list_olympiads,
                dropdown=True,
                label="Select Olympiad",
                class_name="fullwidth",
                on_change=on_selector,
            )
            tgb.chart(figure="{sunburnst_medals}")

    tgb.table(
        "{df_olympic_cities_simplified}",
        filter=True,
    )
