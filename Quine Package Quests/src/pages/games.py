from taipy.gui import  Markdown

from data.data import GAME_DATA

CHESSBOARD_DATA = ""

def on_action(state, _, payload):
    data = GAME_DATA.iloc[payload['index']]
    state.CHESSBOARD_DATA = f'{data.moves}/{data.white_id}/{data.black_id}/{data.white_rating}/{data.black_rating}/{data.victory_status}/{data.winner}/{data.opening_name}'


games = Markdown("src/pages/games.md")