#!/bin/bash
# Generate the React production build and copy it to the top directory
npm run build

cd ../
rm -rf taipy_webapp
cp -R gui/build taipy_webapp
mv taipy_webapp/static/* taipy_webapp
rmdir taipy_webapp/static
