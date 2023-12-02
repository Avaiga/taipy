require("dotenv").config();
const { exec, execSync } = require("child_process");
const { existsSync, writeFileSync, appendFileSync } = require("fs");
const { sep } = require("path");

const getGuiEnv = () =>
    execSync(
        process.platform === "win32"
            ? 'pipenv run pip show taipy-gui | findStr "Location:"'
            : "pipenv run pip show taipy-gui | grep Location:"
    )
        .toString()
        .trim()
        .substring(9)
        .trim();

let TAIPY_GUI_DIR = process.env.TAIPY_GUI_DIR;
if (!TAIPY_GUI_DIR) {
    TAIPY_GUI_DIR = getGuiEnv();
    if (existsSync(".env")) {
        appendFileSync(".env", `\nTAIPY_GUI_DIR=${TAIPY_GUI_DIR}`);
    } else {
        writeFileSync(".env", `TAIPY_GUI_DIR=${TAIPY_GUI_DIR}`);
    }
}

const taipy_webapp_dir = `${TAIPY_GUI_DIR}${sep}taipy${sep}gui${sep}webapp`;
if (!existsSync(taipy_webapp_dir)) {
    console.error(
        `Cannot find the Taipy GUI (${taipy_webapp_dir}) webapp directory.\nMake sure TAIPY_GUI_DIR is set properly as (${getGuiEnv()}).`
    );
    process.exit(1);
}

const spinner = "|/-\\";
let i = 0;

let spinnerTimer;

exec(`npm i ${taipy_webapp_dir}`)
    .on("spawn", () => {
        spinnerTimer = setInterval(() => {
            process.stdout.write("Installing the Taipy GUI library... \r" + spinner[i++]);
            i = i % spinner.length;
        }, 150);
    })
    .on("exit", (code, signal) => {
        clearInterval(spinnerTimer);
        if (code === 0) {
            console.log("\nInstallation finished");
        } else {
            console.log(`\nInstallation failed (code ${code}, signal ${signal})`);
        }
    });
