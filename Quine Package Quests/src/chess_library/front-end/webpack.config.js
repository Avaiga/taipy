const webpack = require("webpack");
const path = require("path");
require("dotenv").config();

module.exports = (_env, options) => {
  return {
    mode: options.mode,
    entry: ["./src/index.ts"],
    output: {
      filename: "library.js",
      path: path.resolve(__dirname, "dist"),
      library: {
        name: "ChessLibrary",
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
      extensions: [".ts", ".tsx"],
    },

    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: "ts-loader",
          exclude: /node_modules/,
        },
        {
          test: /\.css$/i,
          use: [
            "style-loader",
            {
              loader: "css-loader",
              options: {
                modules: true,
              },
            },
          ],
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
    ],
  };
};
