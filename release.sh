# This script is used to release Taipy package
# Required (NPM, Node.JS)

cd gui
npm install
npm run build

cd ../taipy/gui
rm .gitignore
