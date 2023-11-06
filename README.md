<br>
<br>

<img align="left" src="readme_img/readme_logo.png" alt="Taipy Logo" width="20%" ></img>
<br>
#  Welcome to Taipy - Your Web Application Builder
<p align="left">
    <a href="https://pypi.python.org/pypi/taipy/" alt="Taipy version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/taipy.svg?label=pip&logo=PyPI&color=ff462b&labelColor=283282"></a>
    <a href="https://pypi.org/project/taipy" alt="Python version">
        <img alt="PyPI" src="https://img.shields.io/pypi/pyversions/taipy?color=ff462b&labelColor=283282"></a>
    <a href="https://www.youtube.com/@taipy8009" alt="YouTube">
        <img src="https://img.shields.io/badge/youtube-click_to_watch_videos-red.svg?color=ff462b&labelColor=283282&logo=youtube" /></a>
     <a href="https://twitter.com/Taipy_io" alt="Twitter">
        <img src="https://img.shields.io/badge/twitter-click_for_tweets-red.svg?color=ff462b&labelColor=283282&logo=twitter" /></a>


<br>

###  <div align="left">Pure Python & Open-Source. <div align="left"> How? Taipy covers front-end, back-end, and deployment to build production-ready web applications.

<br>

#  <div align="center"> 📊 We make both ends meet ⚙️ </div>
<br>
 <div align="center">

| User Interface Generation  | Scenario and Data Management |
| --------  | -------- |
|<img src="readme_img/gui_creation.webp" alt="Interface Animation"  width="100%"/> | <img src="readme_img/scenario_and_data_mgt.gif" alt="Back-End Animation"  width="70%"/>


</div>

<br>
<br>

## Installation

Open a terminal and run:

```bash
$ pip install taipy
```

*You're all set! All aboard the Taipy journey 🚂*

<br>

## Community

Join our [Discord](https://discord.gg/XcFhrJZru3) to give us feedback, share your creations or just to have a chat with us.

<br>

## Ready, Set, GUI

### Tiny User Interface Demo

```python
from taipy import Gui

excitement_page = """
# Welcome to Taipy
## Getting started with Taipy
### How excited are you to try Taipy?

<|{excitement}|slider|min=1|max=100|>

My excitement level: <|{excitement}|>
"""
excitement = 100

Gui(page=excitement_page).run()
```
*RUN*🏃🏽‍♀️
<div align="center">🎊 TA-DA! 🎊</div>
<br>
<div align="center"><img src="readme_img/readme_fe_app.gif" width="50%" alt="Tiny Demo"></img></div>

<br>

***<div align="center">Check out our [Getting Started](https://docs.taipy.io/en/latest/getting_started/) and [Documentation](https://docs.taipy.io/en/latest/manuals/gui/)</div>***

<br>
<br>

## Scenario and Data Management ⚙️

**<div align="left">Let's create a *Scenario* in Taipy to filter movie data based on the genre you choose. This scenario models a simple pipeline. It is submitted (for execution) each time the genre selection changes and outputs the seven most popular movies of that genre. </div>**

<br>

<div align="center"> ⚠️ Here, the back-end involves the execution of a very simple pipeline (made of a single task). Note that Taipy is designed to build much more complex pipelines 🚀 (with many tasks!) </div>

<br>
<br>

*Here is our filter function: a standard Python function that is used by the unique task in the scenario*
```python
def filter_genre(initial_dataset: pd.DataFrame, selected_genre):
    filtered_dataset = initial_dataset[initial_dataset['genres'].str.contains(selected_genre)]
    filtered_data = filtered_dataset.nlargest(7, 'Popularity %')
    return filtered_data
```

*This is the execution graph of the scenario we are implementing*

<div align="center"><img src="readme_img/readme_exec_graph.png" alt="Demo Execution Graph"  width="80%"/></div>


### Taipy Studio - The easy peasy way
*You can use the Taipy Studio extension in VSCode to configure your sequence with no code*

<div align="center"><img src="readme_img/readme_demo_studio.gif" width="80%" alt="Demo Studio Gif"></img></div>

*Your configuration is automatically saved as a TOML file*

<br>

***<div align="center">Check out our [Documentation](https://docs.taipy.io/en/latest/manuals/studio/) </div>***

<br>
<br>

### Taipy Scenario & Data Management - a walk on the code side
<div align="left">For more advanced use cases or if you prefer coding your configurations instead of using Taipy Studio, Taipy has your back! </div>

*<div align="left">Check out the movie genre demo scenario creation with this [Demo](https://www.taipy.io/project/movie-genre-selector/) </div>*

<br>

***<div align="center">Check out our [Getting Started](https://docs.taipy.io/en/latest/getting_started/) and [Documentation](https://docs.taipy.io/en/latest/manuals/core/) </div>***

<br>
<br>


## User Interface Generation ➕ Scenario & Data Management
*Now, let's load this configuration and add a user interface on top for a 🎉FULL APPLICATION🎉*
```python
import taipy as tp
import pandas as pd
from taipy import Config, Scope, Gui

# TAIPY Scenario & Data Management

# Filtering function - task
def filter_genre(initial_dataset: pd.DataFrame, selected_genre):
    filtered_dataset = initial_dataset[initial_dataset["genres"].str.contains(selected_genre)]
    filtered_data = filtered_dataset.nlargest(7, "Popularity %")
    return filtered_data

# Load the configuration made with Taipy Studio
Config.load("config.toml")
scenario_cfg = Config.scenarios["scenario"]

# Start Taipy Core service
tp.Core().run()

# Create a scenario
scenario = tp.create_scenario(scenario_cfg)


# TAIPY User Interface
# Let's add a GUI to our Scenario Management for a full application

# Callback definition - submits scenario with genre selection
def on_genre_selected(state):
    scenario.selected_genre_node.write(state.selected_genre)
    tp.submit(scenario)
    state.df = scenario.filtered_data.read()

# Get list of genres
genres = [
    "Action", "Adventure", "Animation", "Children", "Comedy", "Fantasy", "IMAX"
    "Romance","Sci-FI", "Western", "Crime", "Mystery", "Drama", "Horror", "Thriller", "Film-Noir","War", "Musical", "Documentary"
    ]

# Initialization of variables
df = pd.DataFrame(columns=["Title", "Popularity %"])
selected_genre = "Action"

## Set initial value to Action
def on_init(state):
    on_genre_selected(state)

# User interface definition
my_page = """
# Film recommendation

## Choose your favorite genre
<|{selected_genre}|selector|lov={genres}|on_change=on_genre_selected|dropdown|>

## Here are the top seven picks by popularity
<|{df}|chart|x=Title|y=Popularity %|type=bar|title=Film Popularity|>
"""

Gui(page=my_page).run()

```
*RUN*🏃🏽‍♀️

<br>

<div align="center">🎊TA-DA!🎊</div>
<br>
<div align="center"><img src="readme_img/readme_app.gif" width="80%" alt="Image of a Taipy demonstration application"></img></div>

<br>

<br>

## ☁️Taipy Cloud☁️
With Taipy Cloud, you can deploy your Taipy applications in a *few clicks* and *for free*!

<div align="center"><img src="readme_img/readme_cloud_demo.gif" alt="Demonstration of Taipy Cloud" width="60%" ></img></div>

<br>
<br>

***<div align="center"> Click [here](https://www.taipy.io/taipy-cloud/) to get started for free </div>***

<br>
<br>


## Contributing ⚒⚒

Want to help build _Taipy_? Check out our [`CONTRIBUTING.md`](CONTRIBUTING.md) file.

## Code of conduct

Want to be part of the _Taipy_ community? Check out our [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) file.

## License
Copyright 2023 Avaiga Private Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at
[http://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
