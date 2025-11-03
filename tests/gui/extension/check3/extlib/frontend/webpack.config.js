/*
 * Test webpack config file.
 */

module.exports = (_env, options) => {
  return {
    entry: ["./src/index.ts"],
    output: {
      filename: "test.js",
      path: path.resolve(__dirname, "testdist"),
      library: {
        name: "FailingName",
      },
    },
  };
};
