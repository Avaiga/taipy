/*
 * Copyright 2023 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

const webpack = require("webpack");
const path = require("path");
const ESLintPlugin = require("eslint-webpack-plugin");
require("dotenv").config();

module.exports = (_env, options) => {
    return {
        mode: options.mode, // "development" | "production"
        entry: ["./src/index.ts"],
        output: {
            filename: "taipy-gui-core.js",
            path: path.resolve(__dirname, "../../taipy/gui_core/lib"),
            library: {
                // Camel case transformation of the library name "example"
                name: "TaipyGuiCore",
                type: "umd",
            },
            publicPath: "/",
        },
        // The Taipy GUI library is indicated as external so that it is
        // excluded from bundling.
        externals: { "taipy-gui": "TaipyGui" },

        // Enable sourcemaps for debugging webpack's output.
        devtool: options.mode === "development" && "inline-source-map",
        resolve: {
            // All the code is TypeScript
            extensions: [".ts", ".tsx", ".js"],
        },

        module: {
            rules: [
                {
                    test: /\.tsx?$/,
                    use: "ts-loader",
                    exclude: /node_modules/,
                },
            ],
        },

        plugins: [
            new webpack.DllReferencePlugin({
                // We assume the current directory is original directory in the taipy-gui repository.
                // If this file is moved, this path must be updated
                manifest: path.resolve(
                    __dirname,
                    `${process.env.TAIPY_DIR}/taipy/gui/webapp/taipy-gui-deps-manifest.json`
                ),
                name: "TaipyGuiDependencies",
            }),
            new ESLintPlugin({
                extensions: [`ts`, `tsx`],
                exclude: [`/node_modules/`],
                eslintPath: require.resolve("eslint"),
            }),
        ],
    };
};
