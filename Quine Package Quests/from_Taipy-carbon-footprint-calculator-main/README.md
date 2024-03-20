# Carbon Footprint Calculator

## Description

The Carbon Footprint Calculator is a web application developed using the Taipy Python library to empower users with insights into their environmental impact based on lifestyle choices. By allowing users to input preferences in key areas such as transportation, energy consumption, diet, and more, the application calculates their total carbon emissions.

## Demo

![Project demo](demo.gif)

## Directory Structure

- `src/`: Contains the source code.
  - `src/data`: Contains the dataset used for the project.
  - `src/main.py`: The main file of the project.
  - `src/model.pkl`: A pretrained model for predictions. You can train your own.
  - `src/requirements.txt`: Project requirements.
- `LICENSE`: The MIT License.
- `README.md`: Current file.

## Installation

This project works with a Python version superior to 3.8. To avoid any issue, set it up in a new virtual environment.

```
git clone https://github.com/vivienogoun/carbon-footprint-calculator.git
cd carbon-footprint-calculator/src
pip install -r requirements.txt
```

## How to run

```
taipy run main.py
```

## Contributing

Contributions are welcome! Feel free to fork the repository, open issues, and submit pull requests to improve existing features or add more features to the project.

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit)
