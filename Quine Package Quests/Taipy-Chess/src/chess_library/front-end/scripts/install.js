require("dotenv").config();
const { exec, execSync } = require("child_process");
const { existsSync, writeFileSync, appendFileSync } = require("fs");
const { sep, resolve } = require("path");

const getGuiEnv = (log = true) => {
  try {
    const pipGuiDir = execSync(
      process.platform === "win32"
        ? 'pip show taipy-gui | findStr "Location:"'
        : "pip show taipy-gui | grep Location:",
      {
        stdio: ["pipe", "pipe", "pipe"],
      }
    )
      .toString()
      .trim();
    return pipGuiDir.substring(9).trim();
  } catch (e) {
    log && console.info("taipy-gui pip package is not installed.");
    const base = existsSync("package.json")
      ? `..${sep}..`
      : existsSync("frontend")
      ? "."
      : sep;
    if (existsSync(resolve(base, "taipy", "gui", "webapp", "package.json"))) {
      log &&
        console.info(
          `Found npm package for taipy-gui in ${resolve(
            base,
            "taipy",
            "gui",
            "webapp"
          )}`
        );
      return base;
    } else {
      log &&
        console.warn(
          `taipy-gui npm package should be built locally in ${resolve(
            base,
            "taipy",
            "gui",
            "webapp"
          )} first.`
        );
    }
  }
  return sep;
};

let taipyEnvDir = process.env.TAIPY_DIR;
if (!taipyEnvDir) {
  taipyEnvDir = getGuiEnv();
  if (taipyEnvDir != sep) {
    if (existsSync(".env")) {
      appendFileSync(".env", `\nTAIPY_DIR=${taipyEnvDir}`);
    } else {
      writeFileSync(".env", `TAIPY_DIR=${taipyEnvDir}`);
    }
  }
}

const taipyWebappDir = `${taipyEnvDir}${sep}taipy${sep}gui${sep}webapp`;
if (!existsSync(taipyWebappDir)) {
  console.error(
    `Cannot find the Taipy GUI (${taipyWebappDir}) webapp directory.\nMake sure TAIPY_DIR is set properly as (${getGuiEnv(
      false
    )}).`
  );
  process.exit(1);
}

const spinner = "|/-\\";
let i = 0;

let spinnerTimer;

exec(`npm i ${taipyWebappDir}`)
  .on("spawn", () => {
    spinnerTimer = setInterval(() => {
      process.stdout.write(
        "Installing the Taipy GUI library... \r" + spinner[i++]
      );
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
