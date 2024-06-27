/*
 * Copyright 2021-2024 Avaiga Private Limited
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

// webpack should be in the node_modules directory, install if not.
const path = require("path");
const webpack = require("webpack");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const AddAssetHtmlPlugin = require('add-asset-html-webpack-plugin');
const ESLintPlugin = require("eslint-webpack-plugin");
const GenerateJsonPlugin = require('generate-json-webpack-plugin');

const resolveApp = relativePath => path.resolve(__dirname, relativePath);

const reactBundle = "taipy-gui-deps"
const taipyBundle = "taipy-gui"

const reactBundleName = "TaipyGuiDependencies"
const taipyBundleName = "TaipyGui"
const taipyGuiBaseBundleName = "TaipyGuiBase"

const basePath = "../../taipy/gui/webapp";
const webAppPath = resolveApp(basePath);
const reactManifestPath = resolveApp(basePath + "/" + reactBundle + "-manifest.json");
const reactDllPath = resolveApp(basePath + "/" + reactBundle + ".dll.js")
const taipyDllPath = resolveApp(basePath + "/" + taipyBundle + ".js")
const taipyGuiBaseExportPath = resolveApp(basePath + "/taipy-gui-base-export");

module.exports = (env, options) => {
    const envVariables = {
        frontend_version: require(resolveApp('package.json')).version,
        frontend_build_date: new Date().toISOString(),
        frontend_build_mode: options.mode
    };

    return [{
            mode: options.mode, //'development', //'production',
            name: reactBundleName,
            entry: ["react", "react-dom",
            "@emotion/react","@emotion/styled",
            "@mui/icons-material","@mui/material","@mui/x-date-pickers", "@mui/x-tree-view"],
            output: {
                filename: reactBundle + ".dll.js",
                path: webAppPath,
                library: reactBundleName,
                publicPath: "",
            },
            plugins: [
                new webpack.DllPlugin({
                    name: reactBundleName,
                    path: reactManifestPath
                })
            ]
        },
        {
            mode: options.mode, //'development', //'production',
            name: taipyBundleName,
            entry: ["./src/extensions/exports.ts"],
            output: {
                filename: taipyBundle + ".js",
                path: webAppPath,
                library: {
                    name: taipyBundleName,
                    type: "umd"
                },
                publicPath: "",
            },
            dependencies: [reactBundleName],
            devtool: options.mode === "development" && "inline-source-map",
            resolve: {
                // Add '.ts' and '.tsx' as resolvable extensions.
                extensions: [".ts", ".tsx", ".js"],
            },
            module: {
                rules: [
                    {
                        test: /\.tsx?$/,
                        use: "ts-loader",
                        exclude: /node_modules/,
                    },
                    {
                        // added to resolve apache-arrow library (don't really understand the problem tbh)
                        // Reference: https://github.com/graphql/graphql-js/issues/2721
                        test: /\.m?js/,
                        resolve: {
                            fullySpecified: false,
                        },
                    },
                ]
            },
            plugins: [
                new ESLintPlugin({
                    extensions: [`ts`, `tsx`],
                    exclude: [`/node_modules/`],
                    eslintPath: require.resolve("eslint"),
                }),
                new webpack.DllReferencePlugin({
                    name: reactBundleName,
                    manifest: reactManifestPath
                })
            ]
        },
        {
            mode: options.mode, //'development', //'production',
            context: resolveApp("dom"),
            entry: ["./src/index.tsx"],
            output: {
                filename: "taipy-gui-dom.js",
                path: webAppPath,
                publicPath: "",
            },
            dependencies: [taipyBundleName, reactBundleName],
            externals: {"taipy-gui": taipyBundleName},

            // Enable sourcemaps for debugging webpack's output.
            devtool: options.mode === "development" && "inline-source-map",

            resolve: {
                // Add '.ts' and '.tsx' as resolvable extensions.
                extensions: [".webpack.js", ".web.js", ".ts", ".tsx", ".js"],
            },
            module: {
                rules: [
                    {
                        test: /\.tsx?$/,
                        use: "ts-loader",
                        exclude: /node_modules/,
                    },
                ]
            },

            plugins: [
                new CopyWebpackPlugin({
                    patterns: [
                        { from: "../public", filter: (name) => !name.endsWith(".html") },
                        { from: "../packaging", filter: (name) => !name.includes(".gen.") }
                    ],
                }),
                new HtmlWebpackPlugin({
                    template: "../public/index.html",
                    hash: true,
                    ...envVariables
                }),
                new GenerateJsonPlugin("taipy.status.json", envVariables),
                new ESLintPlugin({
                    extensions: [`ts`, `tsx`],
                    exclude: [`/node_modules/`],
                    eslintPath: require.resolve("eslint"),
                }),
                new webpack.DllReferencePlugin({
                    name: reactBundleName,
                    manifest: reactManifestPath
                }),
                new AddAssetHtmlPlugin([{
                    filepath: reactDllPath,
                    hash: true
                },{
                    filepath: taipyDllPath,
                    hash: true
                }]),
            ],
    },
    {
        mode: options.mode,
        target: "web",
        entry: {
            "default": "./base/src/index.ts",
            "preview": "./base/src/index-preview.ts",
        },
        output: {
            filename: (arg) => {
                if (arg.chunk.name === "default") {
                    return "taipy-gui-base.js";
                }
                return "[name].taipy-gui-base.js";
            },
            chunkFilename: "[name].taipy-gui-base.js",
            path: webAppPath,
            globalObject: "this",
            library: {
                name: taipyGuiBaseBundleName,
                type: "umd",
            },
        },
        optimization: {
            splitChunks: {
                chunks: 'all',
                name: "shared",
            },
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
        resolve: {
            extensions: [".tsx", ".ts", ".js", ".tsx"],
        },
        // externals: {
        //     "socket.io-client": {
        //         commonjs: "socket.io-client",
        //         commonjs2: "socket.io-client",
        //         amd: "socket.io-client",
        //         root: "_",
        //     },
        // },
    },
    {
        entry: "./base/src/exports.ts",
        output: {
            filename: "taipy-gui-base.js",
            path: taipyGuiBaseExportPath,
            library: {
                name: taipyGuiBaseBundleName,
                type: "umd",
            },
            publicPath: "",
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
        resolve: {
            extensions: [".tsx", ".ts", ".js", ".tsx"],
        },
        plugins: [
            new CopyWebpackPlugin({
                patterns: [
                    { from: "./base/src/packaging", to: taipyGuiBaseExportPath },
                ],
            }),
        ],
    }];
};
