const path = require("path");
const webpack = require("webpack");
const resolveApp = relativePath => path.resolve(__dirname, relativePath);

const moduleName = "TaipyGuiBase";
const basePath = "../../../taipy/gui/webapp";
const webAppPath = resolveApp(basePath);

module.exports = {
    target: "web",
    entry: "./base/src/index.ts",
    output: {
        filename: "taipy-gui-base.js",
        path: webAppPath,
        globalObject: "this",
        library: {
            name: moduleName,
            type: "umd",
        },
    },
    plugins: [
        new webpack.optimize.LimitChunkCountPlugin({
            maxChunks: 1,
        }),
    ],
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
};
