require("dotenv").config();
const { exec, execSync } = require("child_process");
const { existsSync } = require('fs')

const TAIPY_GUI_DIR = process.env.TAIPY_GUI_DIR || execSync(process.platform === "win32" ? 'pipenv run pip show taipy-gui | findStr "Location:"' : "pipenv run pip show taipy-gui | grep Location:").toString().trim().substring(9).trim();

taipy_webapp_dir = `${TAIPY_GUI_DIR}/taipy/gui/webapp`
if (!existsSync(taipy_webapp_dir)) {
  console.error(`Cannot find the Taipy GUI (${taipy_webapp_dir}) webapp directory.\nMake sure TAIPY_GUI_DIR is set properly.`);
  process.exit(1);
}

let spinner = "|/-\\";
let i = 0;

let spinnerTimer;

exec(`npm i && npm i ${taipy_webapp_dir}`)
  .on("spawn", () => {
    spinnerTimer = setInterval(() => {
      process.stdout.write("Installing the Taipy GUI library... \r" + spinner[i++]);
      i = i % spinner.length;
    }, 150);
  })
  .on("exit", (code) => {
    clearInterval(spinnerTimer);
    if (code === 0) {
      console.log("\nInstallation finished");
    } else {
      console.log(`\nInstallation failed (code ${code})`);
    }
  });
