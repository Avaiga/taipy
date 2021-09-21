// webpack should be in the node_modules directory, install if not.
const path = require('path');
const webpack = require("webpack");
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const Dotenv = require('dotenv-webpack');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = (env, options) => ({
    mode: options.mode, //'development', //'production',
    entry: [
        "./src/index.tsx"
    ],
    output: {
        filename: "taipy.js",
        path: path.resolve(__dirname, '../taipy_webapp'),
        library: "Taipy",
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
                enforce: 'pre',
                use: [
                  {
                    options: {
                      eslintPath: require.resolve('eslint'),

                    },
                    loader: require.resolve('eslint-loader'),
                  },
                ],
                exclude: /node_modules/,
            },
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                test: /\.css$/,
                use: [ MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader' ]
            }
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
        new MiniCssExtractPlugin()
    ]
});
