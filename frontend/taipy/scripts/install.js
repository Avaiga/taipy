require("dotenv").config();
const { exec, execSync } = require("child_process");
const { existsSync, writeFileSync, appendFileSync } = require("fs");
const { sep, resolve } = require("path");

/**
 * Get the installation directory of the Taipy GUI.
 * 
 * @param {boolean} log - Whether to log messages to the console.
 * @returns {string} - The path to the Taipy GUI installation directory.
 */
const getGuiEnv = (log = true) => {
    try {
        // Determine command based on the platform
        const command = process.platform === "win32"
            ? 'pip show taipy-gui | findStr "Location:"'
            : "pip show taipy-gui | grep Location:";

        const pipGuiDir = execSync(command, { stdio: ["pipe", "pipe", "pipe"] })
            .toString()
            .trim()
            .substring(9) // Skip the "Location: " part
            .trim();

        return pipGuiDir; // Return the directory path
    } catch (e) {
        if (log) {
            console.info("Taipy GUI pip package is not installed.");
        }
        
        // Determine the base directory to look for npm package
        const base = existsSync("package.json") ? ..${sep}.. : existsSync("frontend") ? "." : sep;

        // Check for the existence of the npm package
        if (existsSync(resolve(base, "taipy", "gui", "webapp", "package.json"))) {
            if (log) {
                console.info(Found npm package for Taipy GUI in ${resolve(base, "taipy", "gui", "webapp")});
            }
            return base; // Return the base directory
        } else {
            if (log) {
                console.warn(Taipy GUI npm package should be built locally in ${resolve(base, "taipy", "gui", "webapp")} first.);
            }
        }
    }
    return sep; // Return the path separator if nothing is found
};

// Set up the TAIPY_DIR environment variable
let taipyEnvDir = process.env.TAIPY_DIR || getGuiEnv();
if (taipyEnvDir !== sep) {
    // Update .env file with the TAIPY_DIR if it's found
    const envContent = TAIPY_DIR=${taipyEnvDir};
    if (existsSync(".env")) {
        appendFileSync(".env", \n${envContent});
    } else {
        writeFileSync(".env", envContent);
    }
}

// Construct the path to the Taipy GUI webapp directory
const taipyWebappDir = ${taipyEnvDir}${sep}taipy${sep}gui${sep}webapp;

// Verify the existence of the webapp directory
if (!existsSync(taipyWebappDir)) {
    console.error(Cannot find the Taipy GUI (${taipyWebappDir}) webapp directory.\nMake sure TAIPY_DIR is set properly as (${getGuiEnv(false)}).);
    process.exit(1);
}

// Spinner setup for installation progress
const spinner = "|/-\\";
let spinnerIndex = 0;
let spinnerTimer;

// Execute npm install command for the Taipy GUI webapp
exec(npm i ${taipyWebappDir})
    .on("spawn", () => {
        // Start the spinner to show installation progress
        spinnerTimer = setInterval(() => {
            process.stdout.write(Installing the Taipy GUI library... \r${spinner[spinnerIndex++]});
            spinnerIndex %= spinner.length; // Loop through the spinner characters
        }, 150);
    })
    .on("exit", (code, signal) => {
        // Clear spinner and log the installation result
        clearInterval(spinnerTimer);
        if (code === 0) {
            console.log("\nInstallation finished");
        } else {
            console.log(\nInstallation failed (code ${code}, signal ${signal}));
        }
    });
