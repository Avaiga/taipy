import pandas as pd
import plotly.express as px
import taipy.gui.builder as tgb

###########################################################
###                    Load Datasets                    ###
###########################################################
df_olympic_medals = pd.read_csv("./data/olympic_medals.csv")

###########################################################
###             Ceate transformed DataFrames            ###
###########################################################
df_grouped_medals = (
    df_olympic_medals.groupby(["Committee", "Medal_type"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
df_grouped_medals["Total"] = (
    df_grouped_medals["Gold"]
    + df_grouped_medals["Silver"]
    + df_grouped_medals["Bronze"]
)


###########################################################
###                      Functions                      ###
###########################################################


def plot_total_medals_by_country(
    df_medals, committee_list, season, medal_type="All", percentage="Total medals"
):
    """
    Plot total medals won by selected committees over Olympic years (by olympic season winter/summer).

    Parameters:
    - df_medals (DataFrame): DataFrame containing medal data.
    - committee_list (list): List of committees to plot.
    - season (str): Olympic season: "summer" or "winter".
    - medal_type (str): Type of medal. Default is "All".
    - percentage (str): Type of representation. Default is "Total medals". Other option is "Percentage"

    Returns:
    - fig: Plotly figure object showing total medals by year for selected committees.
    """

    df_filtered = df_medals[df_medals["Olympic_season"] == season]
    if medal_type != "All":
        df_filtered = df_filtered[df_filtered["Medal_type"] == medal_type]

    # use df_max to calculate percentages:
    df_max = df_filtered.groupby(["Olympic_year", "Olympiad", "Committee"]).size()
    df_max = (
        df_max.groupby(level=["Olympic_year", "Olympiad"])
        .sum()
        .reset_index(name="Total_medals")
    )

    df_filtered = df_filtered[df_filtered["Committee"].isin(committee_list)]

    # If a selected committee is not in the DataFrame, exclude from the list
    committee_list = list(set(df_filtered["Committee"].to_list()))

    # Aggregating total medals for each Olympic year
    df_totals = (
        df_filtered.groupby(["Olympic_year", "Olympiad", "Committee"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    df_totals = df_totals.merge(df_max, on=["Olympic_year", "Olympiad"], how="left")

    if percentage == "Percentage":
        # Calculate the percentage for each committee in each year
        for committee in committee_list:
            df_totals[committee] = (
                df_totals[committee] * 100 / df_totals["Total_medals"]
            )
        value_label = "Percentage of Medals"
    else:
        value_label = "Total Medals"

    fig = px.line(
        df_totals,
        x="Olympic_year",
        y=committee_list,
        labels={
            "value": value_label,
            "variable": "Committee",
            "Olympic_year": "Year",
            "Olympiad": "Olympiad",
        },
        title=f"{medal_type} Medals for Selected committees by Olympic Year | {season}",
        hover_data={"Olympiad": True},
    )

    fig.update_traces(mode="markers+lines", marker=dict(size=4))

    return fig


def plot_medals_grid(df_medals, committee, season):
    """
    Plot medals won by a committee across different disciplines and Olympiads.

    Parameters:
    - df_medals (DataFrame): DataFrame containing medal data.
    - committee (str): Name of the committee.
    - season (str): Olympic season: "summer" or "winter".

    Returns:
    - fig: Plotly figure object showing medals by Olympiad and discipline for the committee.
    """
    # Filter DataFrame by season
    df_filtered = df_medals[(df_medals["Olympic_season"] == season)]

    # Get all possible disciplines --> Like this, all disciplines appear for all countries
    # Important to do this after filtering by season and before filtering by committee!
    all_disciplines = df_filtered["Discipline"].unique()

    # And then only filter the DataFrame by committee
    df_filtered = df_filtered[(df_filtered["Committee"] == committee)]

    # Group by Olympiad and Discipline, then count occurrences
    df_grouped = (
        df_filtered.groupby(["Olympiad", "Olympic_year", "Discipline"])
        .size()
        .unstack(fill_value=0)
    )
    # Sort the index by "Olympic_year"
    df_grouped = df_grouped.sort_index(level=1)
    ordered_olympiads = df_grouped.index.get_level_values("Olympiad").unique()

    # Add all the disciplines of the selcted season, whether the Committee won a medals or not
    df_grouped = df_grouped.reindex(columns=all_disciplines, fill_value=0)

    fig = px.imshow(
        df_grouped,
        labels=dict(x="Discipline", y="Olympiad", color="Total Medals"),
        x=df_grouped.columns,
        y=list(ordered_olympiads),
        color_continuous_scale="plasma",
        title=f"Medals by Olympiad and discipline for {committee} | {season}",
    )
    # reduce font size:
    fig.update_layout(
        xaxis=dict(tickfont=dict(size=9)),
        yaxis=dict(tickfont=dict(size=9)),
        coloraxis_colorbar=dict(
            tickfont=dict(size=9),
        ),
    )
    return fig


###########################################################
###         Initial variables and selector lists        ###
###########################################################

list_seasons = ["All", "summer", "winter"]
list_medal_types = ["All", "Gold", "Silver", "Bronze"]
list_committees = [
    "Afghanistan",
    "Algeria",
    "Argentina",
    "Armenia",
    "Australasia",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Barbados",
    "Belarus",
    "Belgium",
    "Bermuda",
    "Bohemia",
    "Botswana",
    "Brazil",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cameroon",
    "Canada",
    "Chile",
    "China",
    "Chinese Taipei",
    "Colombia",
    "Costa Rica",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czechia",
    "Czechoslovakia",
    "Denmark",
    "Djibouti",
    "Dominican Republic",
    "East Germany",
    "Ecuador",
    "Egypt",
    "Eritrea",
    "Estonia",
    "Ethiopia",
    "Fiji",
    "Finland",
    "France",
    "Gabon",
    "Georgia",
    "Germany",
    "Ghana",
    "Great Britain",
    "Greece",
    "Grenada",
    "Guatemala",
    "Guyana",
    "Haiti",
    "Hong Kong, China",
    "Hungary",
    "Iceland",
    "Independent Olympic Athletes",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Israel",
    "Italy",
    "Ivory Coast",
    "Jamaica",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kosovo",
    "Kuwait",
    "Kyrgyzstan",
    "Latvia",
    "Lebanon",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malaysia",
    "Mauritius",
    "Mexico",
    "Mixed-NOCs",
    "Moldova",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Morocco",
    "Mozambique",
    "Namibia",
    "Netherlands",
    "Netherlands Antilles",
    "New Zealand",
    "Niger",
    "Nigeria",
    "North Korea",
    "North Macedonia",
    "Norway",
    "Pakistan",
    "Panama",
    "Paraguay",
    "Peru",
    "Philippines",
    "Poland",
    "Portugal",
    "Puerto Rico",
    "Qatar",
    "ROC from the abbreviation for Russian Olympic Committee",
    "Romania",
    "Russia",
    "Samoa",
    "San Marino",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Serbia and Montenegro",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "South Africa",
    "South Korea",
    "Soviet Union",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Sweden",
    "Switzerland",
    "Syria",
    "Tajikistan",
    "Tanzania",
    "Thailand",
    "Togo",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Uganda",
    "Ukraine",
    "Unified Team",
    "United Arab Emirates",
    "United States",
    "Uruguay",
    "Uzbekistan",
    "Venezuela",
    "Vietnam",
    "Virgin Islands",
    "West Germany",
    "West Indies Federation",
    "Yugoslavia",
    "Zambia",
    "Zimbabwe",
]

committees = ["France", "United States"]
committee_detail = "France"
medal_type = "All"
display_percent = "Total medals"

###########################################################
###                  Displayed objects                  ###
###########################################################
summer_medal_by_committee = plot_total_medals_by_country(
    df_olympic_medals, committee_list=committees, season="summer", medal_type=medal_type
)
winter_medal_by_committee = plot_total_medals_by_country(
    df_olympic_medals, committee_list=committees, season="winter", medal_type=medal_type
)

# For detail cards
total_medals_detail = int(
    df_grouped_medals[df_grouped_medals["Committee"] == committee_detail]["Total"].iloc[
        0
    ]
)
gold_medals_detail = int(
    df_grouped_medals[df_grouped_medals["Committee"] == committee_detail]["Gold"].iloc[
        0
    ]
)
silver_medals_detail = int(
    df_grouped_medals[df_grouped_medals["Committee"] == committee_detail][
        "Silver"
    ].iloc[0]
)
bronze_medals_detail = int(
    df_grouped_medals[df_grouped_medals["Committee"] == committee_detail][
        "Bronze"
    ].iloc[0]
)

summer_medal_grid = plot_medals_grid(
    df_olympic_medals, committee=committee_detail, season="summer"
)
winter_medal_grid = plot_medals_grid(
    df_olympic_medals, committee=committee_detail, season="winter"
)


###########################################################
###                  Selector Function                  ###
###########################################################
def on_selector(state):
    state.summer_medal_by_committee = plot_total_medals_by_country(
        df_olympic_medals,
        committee_list=state.committees,
        season="summer",
        medal_type=state.medal_type,
        percentage=state.display_percent,
    )
    state.winter_medal_by_committee = plot_total_medals_by_country(
        df_olympic_medals,
        committee_list=state.committees,
        season="winter",
        medal_type=state.medal_type,
        percentage=state.display_percent,
    )
    state.total_medals_detail = int(
        df_grouped_medals[df_grouped_medals["Committee"] == state.committee_detail][
            "Total"
        ].iloc[0]
    )
    state.gold_medals_detail = int(
        df_grouped_medals[df_grouped_medals["Committee"] == state.committee_detail][
            "Gold"
        ].iloc[0]
    )
    state.silver_medals_detail = int(
        df_grouped_medals[df_grouped_medals["Committee"] == state.committee_detail][
            "Silver"
        ].iloc[0]
    )
    state.bronze_medals_detail = int(
        df_grouped_medals[df_grouped_medals["Committee"] == state.committee_detail][
            "Bronze"
        ].iloc[0]
    )
    state.summer_medal_grid = plot_medals_grid(
        df_olympic_medals, committee=state.committee_detail, season="summer"
    )
    state.winter_medal_grid = plot_medals_grid(
        df_olympic_medals, committee=state.committee_detail, season="winter"
    )


###########################################################
###                      Design Page                    ###
###########################################################


with tgb.Page() as committee_medals:

    tgb.text("Medals Awarded to Committees", class_name="h2")
    tgb.text(
        "This dashboard presents aggregated data for the medals awarded to committees."
    )
    tgb.text(
        "Compare as many committees as needed with multiple selections. You can choose to compare all medals or just one medal color."
    )
    tgb.text(
        "Results can be shown as total medals or as a percentage of total medals per Olympic Games."
    )

    with tgb.layout("1 1 1"):
        with tgb.part():
            tgb.selector(
                value="{committees}",
                lov=list_committees,
                dropdown=True,
                multiple=True,
                label="Select committees",
                class_name="fullwidth",
                on_change=on_selector,
            )
        with tgb.part():
            tgb.selector(
                value="{medal_type}",
                lov=list_medal_types,
                dropdown=True,
                label="Select medal type",
                class_name="fullwidth",
                on_change=on_selector,
            )
        with tgb.part():
            tgb.toggle(
                value="{display_percent}",
                lov=["Total medals", "Percentage"],
                on_change=on_selector,
            )

    with tgb.layout("1 1"):
        with tgb.part():
            tgb.chart(figure="{summer_medal_by_committee}")
        with tgb.part():
            tgb.chart(figure="{winter_medal_by_committee}")

    ########################################################

    tgb.text("Detailed information by committee", class_name="h2")
    tgb.text(
        "Select a country to see total medals and how they distribute accross Olympics and disciplines."
    )
    with tgb.layout("1 1 1 1 1"):
        tgb.selector(
            value="{committee_detail}",
            lov=list_committees,
            dropdown=True,
            label="Select committee for detail",
            class_name="fullwidth",
            on_change=on_selector,
        )
        with tgb.part("card"):
            tgb.text(
                "Gold Medals 🥇",
                class_name="h4",
            )
            tgb.text(
                "{gold_medals_detail}",
                class_name="h4",
            )
        with tgb.part("card"):
            tgb.text(
                "Silver Medals 🥈",
                class_name="h4",
            )
            tgb.text(
                "{silver_medals_detail}",
                class_name="h4",
            )
        with tgb.part("card"):
            tgb.text(
                "Bronze Medals 🥉",
                class_name="h4",
            )
            tgb.text(
                "{bronze_medals_detail}",
                class_name="h4",
            )
        with tgb.part("card"):
            tgb.text(
                "Total Medals 🏟",
                class_name="h4",
            )
            tgb.text(
                "{total_medals_detail}",
                class_name="h4",
            )
    with tgb.layout("1 1"):
        with tgb.part():
            tgb.chart(figure="{summer_medal_grid}")
        with tgb.part():
            tgb.chart(figure="{winter_medal_grid}")
