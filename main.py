import os
os.environ["TAIPY_GUI_WEBAPP_PATH"] = os.path.normpath(r"C:\Users\kript\OneDrive\Desktop\M2S\Maintenance\TaipyThroughCMD\taipy\taipy\gui\webapp")

from taipy.gui import Gui
import taipy.gui.builder as tgb

options = [("a", "Option A"), ("b", "Option BBBBB"), ("c", "Option C"), ("d", "Option D")]


with tgb.Page() as page:
   tgb.menu(label = "options",
            lov = options,
            expanded = True,
)


if __name__ == "__main__":
    Gui(page).run(title="Menu - Selected")
