from taipy.gui import Gui, notify
import taipy.gui.builder as tgb
from script import sentiment_analysis

text = "Original text"

def on_button1_action(state):
    data = sentiment_analysis(state.text, language="English")
    notify(state, 'info', f'Sentiment: {data["sentiment"]} , Confidence: {data["percentage"]}')
    return

def on_button2_action(state):
    data = sentiment_analysis(state.text, language="Hindi")
    notify(state, 'info', f' भाव: {data["sentiment"]} , भरोसा: {data["percentage"]}')
    return


# Definition of the page
with tgb.Page() as page:


    tgb.text("Movie Analysis and Review System!", class_name="h1")

    tgb.text("Enter a Movie Name", class_name="h6")

    tgb.input("{text}")

    tgb.button("Search to get Results in English!", on_action=on_button1_action, )
    
    tgb.button("Search and Get Results in Hindi!", on_action=on_button2_action)

Gui(page).run(port=1000)