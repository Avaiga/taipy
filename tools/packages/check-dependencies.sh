PACKAGES=taipy*/*requirements.txt

# Retrieve requirements then install them to check the latest requirements installable
python check-dependencies.py raw-packages $PACKAGES > requirements.txt.tmp

# Create a virtual environment, install packages, and freeze them
python -m venv tmp-venv > /dev/null
if [ -f "./tmp-venv/bin/python3" ]; then
    ./tmp-venv/bin/python3 -m pip install -r requirements.txt.tmp > /dev/null
    ./tmp-venv/bin/python3 -m pip freeze > real-requirements.txt
else
    ./tmp-venv/Scripts/python.exe -m pip install -r requirements.txt.tmp > /dev/null
    ./tmp-venv/Scripts/python.exe -m pip freeze > real-requirements.txt
fi

# Update requirements based on the latest installable requirements
python check-dependencies.py dependencies-to-update real-requirements.txt $PACKAGES
python check-dependencies.py generate-pipfile $1 real-requirements.txt $PACKAGES
