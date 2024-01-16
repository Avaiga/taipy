PACKAGES="taipy-core/setup.requirements.txt taipy/setup.requirements.txt taipy-gui/setup.requirements.txt taipy-config/setup.requirements.txt taipy-rest/setup.requirements.txt"

# Ensure package are using the same version of dependencies
python check-dependencies.py ensure-same-version $PACKAGES

# Retrieve requirements then install them to check the latest requirements installable
cat $PACKAGES | grep -v "taipy" | grep -Eo "[^>]*" | grep -v "=" > requirements.txt.tmp
python -m venv tmp-venv
./tmp-venv/bin/python -m pip install -r requirements.txt.tmp
./tmp-venv/bin/python -m pip freeze > real-requirements.txt
grep -Ff requirements.txt.tmp real-requirements.txt
rm -rf tmp-venv requirements.txt.tmp

# Update requirements based on the latest installable requirements
python check-dependencies.py dependencies-to-update real-requirements.txt $PACKAGES
