from taipy.gui import  Markdown
import pandas as pd
from data.data import GAME_DATA

labels = ['white', 'black', 'draw']

color_data = {
    "labels": labels,
    "values": GAME_DATA['winner'].value_counts().reindex(labels).fillna(0),
}

color_chart_properties = {
    "data" : color_data,
    "values" : "values",
    "labels" : "labels",
    "options" : {
        "hoverinfo": "label+percent",
        "hole": 0.4,
    },
    "markers" : {
        "colors":   ["#F28585", "#FFA447", "#FFFC9B"],
    },
    "layout" : {
        "title": "Win Percentage by Color"
    },
    "plot_config" : {
        "displayModeBar": False,
    },
}

color_range_properties = {
    "y[1]" : "White",
    "y[2]" : "Black",
    "y[3]" : "Draw",
    "columns": ["White", "Black", "Draw"],
    "x": "Rating",
    "title": "Win Percentage by Rating Range",
    "plot_config" : {
        "editable" : False,
        "scrollZoom": False,
        "displayModeBar": False,
    },
    "layout" : {
        "yaxis" : {
            "title" : "Win Percentage",
        },
        "xaxis" : {
            "title" : "Rating Range",
        },
    },
}

bins = [0, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600]

GAME_DATA['white_rating_range'] = pd.cut(GAME_DATA['white_rating'], bins, include_lowest=True)
GAME_DATA['black_rating_range'] = pd.cut(GAME_DATA['black_rating'], bins, include_lowest=True)

white_wins_by_rating_range = GAME_DATA[GAME_DATA['winner'] == 'white'].groupby(GAME_DATA['white_rating_range'], observed=True).size()
black_wins_by_rating_range = GAME_DATA[GAME_DATA['winner'] == 'black'].groupby(GAME_DATA['black_rating_range'], observed=True).size()
draws_by_rating_range = GAME_DATA[GAME_DATA['winner'] == 'draw'].groupby(GAME_DATA['black_rating_range'], observed=True).size()

total_games_by_rating_range = white_wins_by_rating_range + black_wins_by_rating_range + draws_by_rating_range

white_win_percentages = (white_wins_by_rating_range / total_games_by_rating_range) * 100
black_win_percentages = (black_wins_by_rating_range / total_games_by_rating_range) * 100

wins_by_rating_range= pd.DataFrame({
    "Rating": ["0-1000", "1000-1200", "1200-1400", "1400-1600", "1600-1800", "1800-2000", "2000-2200", "2200-2400", "2400-2600"],
    "White": white_win_percentages,
    "Black": black_win_percentages,
    "Draw": (draws_by_rating_range / total_games_by_rating_range) * 100
})

stats = Markdown("src/pages/stats.md")