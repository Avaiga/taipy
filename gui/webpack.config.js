// webpack should be in the node_modules directory, install if not.
const path = require('path');
const webpack = require("webpack");
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const Dotenv = require('dotenv-webpack');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const ESLintPlugin = require('eslint-webpack-plugin');

module.exports = (env, options) => ({
    mode: options.mode, //'development', //'production',
    entry: [
        "./src/index.tsx"
    ],
    output: {
        filename: "taipy.js",
        path: path.resolve(__dirname, '../taipy/gui/webapp'),
        library: "Taipy",
        publicPath: "/",
        libraryTarget: "umd", //"var" "commonjs" "umd"
    },

    // Enable sourcemaps for debugging webpack's output.
    devtool: options.mode === 'development' && 'inline-source-map',

    resolve: {
        // Add '.ts' and '.tsx' as resolvable extensions.
        extensions: [".webpack.js", ".web.js", ".ts", ".tsx", ".js"]
    },

    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                test: /\.css$/,
                use: [ MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader' ]
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
            patterns: [
            {from: 'public', filter: name => !name.endsWith('.html')},
        ]}),
        new HtmlWebpackPlugin({
            template: 'public/index.html',
            hash: true
        }),
        new Dotenv({
            path: './.env.' + options.mode
        }),
        new MiniCssExtractPlugin(),
        new ESLintPlugin({
            extensions: [`ts`, `tsx`],
            exclude: [
                `/node_modules/`,
              ],
              eslintPath: require.resolve('eslint'),
          })
    ]
});
