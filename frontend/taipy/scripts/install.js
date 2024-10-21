require('dotenv').config();
const { exec, execSync } = require('child_process');
const { existsSync, writeFileSync, appendFileSync } = require('fs');
const { sep, resolve } = require('path');

class TaipyInstaller {
    constructor() {
        this.spinner = ['|', '/', '-', '\\'];
        this.spinnerIndex = 0;
        this.spinnerTimer = null;
    }

    /**
     * Get the Taipy GUI installation directory
     * @param {boolean} log - Whether to log information messages
     * @returns {string} - Installation directory path
     */
    getGuiEnv(log = true) {
        try {
            const command = process.platform === 'win32'
                ? 'pip show taipy-gui | findStr "Location:"'
                : 'pip show taipy-gui | grep Location:';

            const pipGuiDir = execSync(command, { stdio: ['pipe', 'pipe', 'pipe'] })
                .toString()
                .trim()
                .substring(9)
                .trim();

            return pipGuiDir;
        } catch (error) {
            if (log) {
                console.info('taipy-gui pip package is not installed.');
            }

            return this.findLocalPackage(log);
        }
    }

    /**
     * Find local Taipy GUI package
     * @param {boolean} log - Whether to log information messages
     * @returns {string} - Package directory path
     */
    findLocalPackage(log) {
        const base = this.determineBaseDirectory();
        const packagePath = resolve(base, 'taipy', 'gui', 'webapp', 'package.json');

        if (existsSync(packagePath)) {
            log && console.info(`Found npm package for taipy-gui in ${resolve(base, 'taipy', 'gui', 'webapp')}`);
            return base;
        }

        log && console.warn(`taipy-gui npm package should be built locally in ${resolve(base, 'taipy', 'gui', 'webapp')} first.`);
        return sep;
    }

    /**
     * Determine the base directory for package search
     * @returns {string} - Base directory path
     */
    determineBaseDirectory() {
        if (existsSync('package.json')) return `..${sep}..`;
        if (existsSync('frontend')) return '.';
        return sep;
    }

    /**
     * Update or create .env file with TAIPY_DIR
     * @param {string} taipyDir - Directory path to save
     */
    updateEnvFile(taipyDir) {
        const envContent = `TAIPY_DIR=${taipyDir}`;
        
        if (existsSync('.env')) {
            appendFileSync('.env', `\n${envContent}`);
        } else {
            writeFileSync('.env', envContent);
        }
    }

    /**
     * Start the installation spinner
     */
    startSpinner() {
        this.spinnerTimer = setInterval(() => {
            process.stdout.write(`Installing the Taipy GUI library... \r${this.spinner[this.spinnerIndex++]}`);
            this.spinnerIndex %= this.spinner.length;
        }, 150);
    }

    /**
     * Stop the installation spinner
     */
    stopSpinner() {
        if (this.spinnerTimer) {
            clearInterval(this.spinnerTimer);
            this.spinnerTimer = null;
        }
    }

    /**
     * Install Taipy GUI
     */
    async install() {
        try {
            let taipyEnvDir = process.env.TAIPY_DIR;

            if (!taipyEnvDir) {
                taipyEnvDir = this.getGuiEnv();
                if (taipyEnvDir !== sep) {
                    this.updateEnvFile(taipyEnvDir);
                }
            }

            const taipyWebappDir = `${taipyEnvDir}${sep}taipy${sep}gui${sep}webapp`;

            if (!existsSync(taipyWebappDir)) {
                throw new Error(
                    `Cannot find the Taipy GUI (${taipyWebappDir}) webapp directory.\n` +
                    `Make sure TAIPY_DIR is set properly as (${this.getGuiEnv(false)}).`
                );
            }

            return new Promise((resolve, reject) => {
                const installation = exec(`npm i ${taipyWebappDir}`);

                installation.on('spawn', () => this.startSpinner());

                installation.on('exit', (code, signal) => {
                    this.stopSpinner();
                    if (code === 0) {
                        console.log('\nInstallation finished');
                        resolve();
                    } else {
                        console.log(`\nInstallation failed (code ${code}, signal ${signal})`);
                        reject(new Error(`Installation failed with code ${code}`));
                    }
                });

                installation.on('error', (error) => {
                    this.stopSpinner();
                    console.error('\nInstallation error:', error.message);
                    reject(error);
                });
            });
        } catch (error) {
            console.error('Installation failed:', error.message);
            process.exit(1);
        }
    }
}

// Run the installation
const installer = new TaipyInstaller();
installer.install().catch(() => process.exit(1));
