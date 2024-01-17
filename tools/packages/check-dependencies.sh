PACKAGES=taipy-*/*requirements.txt

# Retrieve requirements then install them to check the latest requirements installable
python check-dependencies.py raw-packages $PACKAGES > requirements.txt.tmp
python -m venv tmp-venv > /dev/null
./tmp-venv/bin/python3 -m pip install -r requirements.txt.tmp > /dev/null
./tmp-venv/bin/python3 -m pip freeze > real-requirements.txt
grep -Ff requirements.txt.tmp real-requirements.txt > new-requirements.txt
rm -rf tmp-venv requirements.txt.tmp real-requirements.txt
cat new-requirements.txt
# Update requirements based on the latest installable requirements
python check-dependencies.py dependencies-to-update new-requirements.txt $PACKAGES
