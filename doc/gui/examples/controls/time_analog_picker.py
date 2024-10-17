from datetime import datetime

from taipy.gui import Gui
time = datetime.today()

page = "<|{time}|time|analogic|>"

if __name__ == "__main__":
    Gui(page).run(title="Time - Analog Picker")
