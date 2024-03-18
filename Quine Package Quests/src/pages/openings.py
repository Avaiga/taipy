from taipy.gui import Markdown

from data.data import OPENING_DATA, GAME_DATA

CHESSBOARD_DATA = ""

df_opening_by_wins = GAME_DATA.groupby("opening_name", observed=True)["winner"].value_counts().unstack().fillna(0)
df_opening_by_wins['total_wins'] = df_opening_by_wins['white'] + df_opening_by_wins['black']
df_opening_by_wins = df_opening_by_wins.sort_values('total_wins', ascending=False).reset_index()

def on_action(state, _, payload):
    opening_name = df_opening_by_wins.iloc[payload['index']].opening_name
    data = OPENING_DATA[OPENING_DATA["opening_name"] == opening_name.replace(" | ", ",").replace(":", ",")].iloc[0]
    state.CHESSBOARD_DATA = f'{data.moves}///////{data.opening_name}'

openings = Markdown("src/pages/openings.md")