const path = require("path");
const webpack = require("webpack");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const resolveApp = (relativePath) => path.resolve(__dirname, relativePath);

const moduleName = "TaipyGuiBase";
const basePath = "../../../taipy/gui/webapp";
const webAppPath = resolveApp(basePath);
const taipyGuiBaseExportPath = resolveApp(basePath + "/taipy-gui-base-export");

module.exports = [
    {
        target: "web",
        entry: {
            default: "./base/src/index.ts",
            preview: "./base/src/index-preview.ts",
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
                name: moduleName,
                type: "umd",
            },
        },
        optimization: {
            splitChunks: {
                chunks: "all",
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
        output: { filename: "taipy-gui-base.js", path: taipyGuiBaseExportPath },
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
    },
];
