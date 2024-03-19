from taipy import Gui
from taipy.gui import Html, navigate
import taipy.gui.builder as tgb
import data
import csv
import graphs
import chat
from datetime import datetime
import pandas as pd
import os
import requests
from fossildata import dataset_fossil_fuels_gdp
from pages.carbonfootprint import carbonfootprint_page
from pages.carbonemissions import carbonemissionspage
from pages.oddeven import oddEvencontent
from pages.greenzone import greenZonecontent
from pages.transport import publicTransportcontent
# --------------------------------------------------------- setting up global styling
stylekit = {
  "color_primary": "#FFB6C1",
  "color_secondary": "#FFC0CB",
}
# ---------------------------------------------------------
OE = "OddEven"
PT = "PublicTransport"
EV = "ElectricVehicle"
DATE = "Date"
BREAKTYPE = "Break"

button_ids = {
    "understandSubmit": "OddEven",
    "benefitsSubmit": "OddEven",
    "challengeSubmit": "OddEven",
    "busTrainSubmit": "PublicTransport",
    "bikeScooterSubmit": "PublicTransport",
    "carPoolSubmit": "PublicTransport",
    "evSubmit": "ElectricVehicle",
    "readingSubmit": "ElectricVehicle",
    "greenOfficeSubmit": "ElectricVehicle"
  }

data.refresh_data()

dataframe = pd.DataFrame({DATE:graphs.date_lis,
                          OE:graphs.OE_breaks,
                          EV:graphs.EV_breaks,
                          PT:graphs.PT_breaks})

def add_entry(activity_category):
    current_date = datetime.now().strftime("%m/%d/%y")

    data_list = [current_date, activity_category]

    with open('test.csv', 'a', newline='') as csvfile:
      csv_writer = csv.writer(csvfile)
      csv_writer.writerow(data_list)

def on_action(state, id):
    # Code to update graph
    if id == "loginSubmit":
        pages = dashboardpage
        pass
    elif id == "logoutSubmit":
        pages = loginContent
    elif id in button_ids:
        add_entry(button_ids.get(id))
        navigate(state, "analytics")
        data.refresh_data()
        data_dict = {
            DATE:graphs.get_date_lis(),
            OE:graphs.get_OE(),
            EV:graphs.get_EV(),
            PT:graphs.get_PT()
        }
        state.dataframe = pd.DataFrame(data_dict)


# --------------------------------------------------------- Login Page

loginContent = Html("""""")
# STORE USERNAME AND PASSWORD
user = "user123"
password = "password123"

# navigates to home function
def nav_home(state):
    global user
    global password
    navigate(state, "dashboard")
    pass
def updateUser(state):
    global user
    user = state.user
    print("Current user is: ", user)
def updatePassword(state):
    global password
    password = state.password
    print("Current password is ", password)

loginContent = """
<img style="margin-bottom: 20px; margin-top: 15px; width: 200px; height: auto; margin-right: 20px;" src='images/FuelFree.png' alt="Description of the image"></img>
<h1>Join FuelFree Today</h1>
<p>Username: </p>
<|{user}|input|on_change=updateUser|>
<p>Password: </p>
<|{password}|input|on_change=updatePassword|password=True|>              
<|Login|button|id="loginSubmit"|on_action=nav_home|>
"""


# navigates to home function
def nav_login(state):
    navigate(state, "login")
    pass



# --------------------------------------------------------- Analytics Page
analyticsContent = """
<|toggle|theme|>
<|{dataframe}|chart|properties={data.property_chart}|rebuild|>

"""
# --------------------------------------------------------- Chatbot Page
# chatContent = """"""
chatContent = tgb.Page()
userQuestion = "say hello"
properQuestion = False
prompt = "say hello"
answer = ""
wordCount = 40
def updateUserQuestion(state):
    global userQuestion
    userQuestion = state.userQuestion
    print("Current userQuestion is: ", userQuestion)
    pass

def submitQuestion(state):
    prompt = state.userQuestion
    state.answer = chat.genActivity(prompt + " answered in less than " + str(wordCount) +" words")
    pass


chatContent = """
<|toggle|theme|>
<h1 style="color:yellow;">Introducing FuelFree's chatbot, CarbonCutter!</h1>
<br/>

<p>Hi, I am CarbonCutter, here to help. I can recommend any ElectricVehicle, energetic, or OddEven activities for you to do!</p>
<|{userQuestion}|input|label="ask here"|on_change=updateUserQuestion|>
<|Ask|button|id="questionSubmit"|on_action=submitQuestion|>
<|{answer}|input|multiline|answer|active={prompt!="" and answer!=""}|class_name=fullwidth|>
"""



country = "Spain"
region = "Europe"
lov_region = list(dataset_fossil_fuels_gdp.Entity.unique())


def load_dataset(_country):
    """Load dataset for a specific country.

    Args:
        _country (str): The name of the country.

    Returns:
        pandas.DataFrame: A DataFrame containing the fossil fuels GDP data for the specified country.
    """
    dataset_fossil_fuels_gdp_cp = dataset_fossil_fuels_gdp.reset_index()

    dataset_fossil_fuels_gdp_cp = dataset_fossil_fuels_gdp_cp[
        dataset_fossil_fuels_gdp["Entity"] == _country
    ]
    return dataset_fossil_fuels_gdp_cp


dataset_fossil_fuels_gdp_cp = load_dataset(country)


def on_change_country(state):
    """Update the dataset based on the selected country.

    Args:
        state (object): The "state" of the variables ran by the program (value changes through selectors)

    Returns:
        None
    """
    print("country is:", state.country)
    _country = state.country
    dataset_fossil_fuels_gdp_cp = load_dataset(_country)
    state.dataset_fossil_fuels_gdp_cp = dataset_fossil_fuels_gdp_cp


layout = {"yaxis": {"range": [0, 100000]}, "xaxis": {"range": [1965, 2021]}}

dashboardpage = """
<|toggle|theme|>
# **Fossil Fuel consumption**{: style="color: #7ED957"} by per capita by country*

Data comes from <a href="https://ourworldindata.org/grapher/per-capita-fossil-energy-vs-gdp" target="_blank">Our World in Data</a>


<|{country}|selector|lov={lov_region}|on_change=on_change_country|dropdown|label=Country/Region|>



<|{dataset_fossil_fuels_gdp_cp}|chart|type=plot|x=Year|y=Fossil fuels per capita (kWh)|height=200%|layout={layout}|>

## **Fossil fuel per capita for**{: style="color: #7ED957"}* <|{country}|>:
<|{dataset_fossil_fuels_gdp_cp}|table|height=400px|width=95%|>


"""


# --------------------------------------------------------- Routing between pages
pages = {
    "/": "<|menu|lov={page_names}|on_action=menu_action|>",
    "login": loginContent,
    "dashboard": dashboardpage,
    'carbonemissionspage': carbonemissionspage,
    'carbonfootprint_page': carbonfootprint_page,
    "OddEven": oddEvencontent,
    "PublicTransport": publicTransportcontent,
    "ElectricVehicle": greenZonecontent,
    "analytics": analyticsContent,
    "chat": chatContent,

}
page_names = [page for page in pages.keys() if page != "/"]

def menu_action(state, action, payload):
    page = payload["args"][0]
    navigate(state, page)

# --------------------------------------------------------- Display the GUI

if __name__ == "__main__":
    # Create the Gui instance with the provided pages and stylekit
    gui = Gui(pages=pages)
    
    # Run the GUI with specified parameters
    gui.run(
        run_browser=False,  # Ensure the browser is not opened automatically
        use_reloader=True,  # Set to True if you are in development
        title="FuelFree",       # Set the title of the GUI window
    )
