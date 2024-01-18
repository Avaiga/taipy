# This script is used to check the latest installable requirements for each package.
# It will generate a requirements.txt file without bound for each package.
# Then install and dump them to check the latest installable requirements.
# If the program detect a new package available, it print it on stdout.
# Finally, it will generate a Pipfile with the latest version available.

# Generate requirements.txt without bound.
python check-dependencies.py generate-raw-requirements > raw-requirements.txt

# Create a virtual environment, install dependencies, and freeze them
python -m venv tmp-venv > /dev/null
./tmp-venv/bin/python3 -m pip install -r raw-requirements.txt > /dev/null
./tmp-venv/bin/python3 -m pip freeze > new-requirements.txt

# Display dependencies summary.
python check-dependencies.py dependencies-summary new-requirements.txt

# Generate a Pipfile based on the new dependencies.
python check-dependencies.py generate-pipfile $1 new-requirements.txt

rm -f new-requirements.txt raw-requirements.txt
