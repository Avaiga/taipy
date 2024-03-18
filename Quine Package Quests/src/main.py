from taipy.gui import Gui
from chess_library import ChessLibrary

from pages.root import root
from pages.games import games
from pages.openings import openings
from pages.stats import stats
from pages.board import board

pages = {
    "/": root,
    "Games": games, 
    "Openings": openings,
    "Board": board,
    "Stats": stats,
}

if __name__ == "__main__":
    Gui(pages=pages, libraries=[ChessLibrary()]).run(title="Taipy Chess!", dark_mode=True)