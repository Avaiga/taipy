[![Taipy Designer](https://github.com/Avaiga/taipy/assets/100117126/50cbc1e8-318e-4b40-ae7e-6eebfb933c75)
](https://taipy.io/enterprise)

<div align="center">
  <a href="https://taipy.io?utm_source=github" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Avaiga/taipy/assets/100117126/509bf101-54c2-4321-adaf-a2af63af9682">
    <img alt="Taipy" src="https://github.com/Avaiga/taipy/assets/100117126/4df8a733-d8d0-4893-acf0-d24ef9e8b58a" width="400" />
  </picture>
  </a>
</div>

<h1 align="center">
Data and AI algorithms into production-ready web apps
</h1>

<div align="center">
Taipy is an open-source Python library for easy, end-to-end application development,<br />featuring what-if analyses, smart pipeline execution, built-in scheduling, and deployment tools.
</div>

  <p align="center">
    <br />
    <a href="https://docs.taipy.io/en/latest/"><strong>Explore the docs »</strong></a>
    <br/><br/>
    <a href="https://discord.com/invite/SJyz2VJGxV">Discord support</a>
    ·
    <a href="https://docs.taipy.io/en/latest/gallery/">Demos & Examples</a>
  </p>

&nbsp;

## ⭐️ What's Taipy?

Taipy is designed for data scientists and machine learning engineers to build full-stack apps.
&nbsp;

⭐️ Enables building production-ready web applications.<br />
⭐️ No need to learn new languages or full-stack frameworks.<br />
⭐️ Concentrate on Data and AI algorithms without development and deployment complexities.

&nbsp;

| User Interface Generation  | Scenario and Data Management |
| --------  | -------- |
|<img src="readme_img/gui_creation.webp" alt="Interface Animation"  width="850px" height="250px" /> | <img src="readme_img/scenario_and_data_mgt.gif" alt="Back-End Animation"  width="100%"/>

&nbsp;

## ✨ Features
- **Python-Based UI Framework:** Taipy is designed for Python users, particularly those working in AI and data science. It allows them to create full stack applications without needing to learn additional skills like HTML, CSS, or JavaScript.


- **Pre-Built Components for Data Pipelines:** Taipy includes pre-built components that allow users to interact with data pipelines, including visualization and management tools.


- **Scenario and Data Management Features:** Taipy offers features for managing different business scenarios and data, which can be useful for applications like demand forecasting or production planning.


- **Version Management and Pipeline Orchestration:** It includes tools for managing application versions, pipeline versions, and data versions, which are beneficial for multi-user environments.

&nbsp;

## ⚙️ Quickstart
To install Taipy stable release run:
```bash
pip install taipy
```

To install Taipy on a Conda Environment or from source, please refer to the [Installation Guide](https://docs.taipy.io/en/latest/installation/).<br />
To get started with Taipy, please refer to the [Getting Started Guide](https://docs.taipy.io/en/latest/getting_started/).

&nbsp;

## 🔌 Scenario and Data Management

Let's create a scenario in Taipy that allows you to filter movie data based on your chosen genre.<br />
This scenario is designed as a straightforward pipeline.<br />
Every time you change your genre selection, the scenario runs to process your request.<br />
It then displays the top seven most popular movies in that genre.

<br />

> ⚠️ Keep in mind, in this example, we're using a very basic pipeline that consists of just one task. However,<br />
> Taipy is capable of handling much more complex pipelines 🚀

<br />

Below is our filter function. This is a typical Python function and it's the only task used in this scenario.

```python
def filter_genre(initial_dataset: pd.DataFrame, selected_genre):
    filtered_dataset = initial_dataset[initial_dataset['genres'].str.contains(selected_genre)]
    filtered_data = filtered_dataset.nlargest(7, 'Popularity %')
    return filtered_data
```

This is the execution graph of the scenario we are implementing
<p align="center">
<img src="https://github.com/Avaiga/taipy/raw/develop/readme_img/readme_exec_graph.png" width="600" align="center" />
</p>

### Taipy Studio
You can use the Taipy Studio extension in Visual Studio Code to configure your scenario with no code<br />
Your configuration is automatically saved as a TOML file.<br />
Check out Taipy Studio [Documentation](https://docs.taipy.io/en/latest/manuals/studio/)

For more advanced use cases or if you prefer coding your configurations instead of using Taipy Studio,<br />
Check out the movie genre demo scenario creation with this [Demo](https://docs.taipy.io/en/latest/knowledge_base/demos/movie_genre_selector/).

![TaipyStudio](https://github.com/Avaiga/taipy/raw/develop/readme_img/readme_demo_studio.gif)

&nbsp;

## User Interface Generation and Scenario & Data Management
This simple Taipy application demonstrates how to create a basic film recommendation system using Taipy.<br />
The application filters a dataset of films based on the user's selected genre and displays the top seven films in that genre by popularity.
Here is the full code for both the frontend and backend of the application.

```python
import taipy as tp
import pandas as pd
from taipy import Config, Scope, Gui

# Taipy Scenario & Data Management

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


# Taipy User Interface
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

And the final result:
<img src="readme_img/readme_app.gif" />

&nbsp;

## ☁️ Taipy cloud
With Taipy Cloud, you can deploy your Taipy applications in a few clicks and for free!
To learn more about Taipy Cloud, please refer to the [Taipy Cloud Documentation](https://docs.taipy.io/en/latest/cloud/).

![TaipyCloud](https://github.com/Avaiga/taipy/raw/develop/readme_img/readme_cloud_demo.gif)

## ⚒️ Contributing
Want to help build Taipy? Check out our [Contributing Guide](https://github.com/Avaiga/taipy/blob/develop/CONTRIBUTING.md).

## 🪄 Code of conduct
Want to be part of the Taipy community? Check out our [Code of Conduct](https://github.com/Avaiga/taipy/blob/develop/CODE_OF_CONDUCT.md)

## 🪪 License
Copyright 2021-2024 Avaiga Private Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at
[http://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
