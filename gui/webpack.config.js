/*
 * Copyright 2022 Avaiga Private Limited
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
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const ESLintPlugin = require("eslint-webpack-plugin");

module.exports = (env, options) => {
    return {
        mode: options.mode, //'development', //'production',
        entry: ["./src/index.tsx"],
        output: {
            filename: "taipy.[contenthash].js",
            path: path.resolve(__dirname, "../taipy/gui/webapp"),
            library: "Taipy",
            publicPath: "/",
            libraryTarget: "umd", //"var" "commonjs" "umd"
        },

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
                {
                    test: /\.css$/,
                    use: [MiniCssExtractPlugin.loader, "css-loader", "postcss-loader"],
                },
                {
                    // added to resolve apache-arrow library (don't really understand the problem tbh)
                    // Reference: https://github.com/graphql/graphql-js/issues/2721
                    test: /\.m?js/,
                    resolve: {
                        fullySpecified: false,
                    },
                },
            ],
        },
        plugins: [
            new CopyWebpackPlugin({
                patterns: [{ from: "public", filter: (name) => !name.endsWith(".html") }],
            }),
            new HtmlWebpackPlugin({
                template: "public/index.html",
                hash: false,
            }),
            new MiniCssExtractPlugin(),
            new ESLintPlugin({
                extensions: [`ts`, `tsx`],
                exclude: [`/node_modules/`],
                eslintPath: require.resolve("eslint"),
            }),
        ],
    };
};
