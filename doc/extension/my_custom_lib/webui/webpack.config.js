// webpack should be in the node_modules directory, install if not.
const path = require("path");
const webpack = require("webpack");

module.exports = (env, options) => {
    return {
        mode: options.mode, //'development', //'production',
        entry: ["./src/index.ts"],
        output: {
            filename: "myCustom.js",
            path: path.resolve(__dirname, "dist"),
            library: {
                name: "MyCustom",
                type: "umd"
            },
            publicPath: "/",
        },
	// 'taipy-gui' is declared as external so that it is *not* bundled.
        externals: {"taipy-gui": "TaipyGui"},

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
            ],
        },

        plugins: [
            new webpack.DllReferencePlugin({
		// This pathname should point to the location of <TAIPY_DIR>/webapp/taipy-gui-deps-manifest.json
		// where <TAIPY_DIR> is the installation directory for Taipy GUI on your filesystem.
		// You may want to use the script 'find_taipy_gui_dir.py' to get this information.
                manifest: path.resolve(__dirname, '<TAIPY_GUI_DIR>/webapp/taipy-gui-deps-manifest.json'),
                name: 'TaipyGuiDependencies'
            }),
        ]

    };
};
