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

/** @type {import('ts-jest/dist/types').JestConfigWithTsJest} */
module.exports = {
    // testEnvironment: 'jest-environment-jsdom',
    // preset: "ts-jest",
    preset: "ts-jest/presets/js-with-ts",
    testEnvironment: "jsdom",
    setupFiles: [
        "./test-config/jest.env.js",
        "./test-config/createObjectUrl.js",
        "./test-config/Canvas.js",
        "./test-config/mockFileUpload.js",
        "./test-config/intersectionObserver.js",
    ],
    coverageReporters: ["json", "html", "text"],
    transformIgnorePatterns: ["<rootDir>/node_modules/(?!react-jsx-parser/)"],
    transform: {
        "^.+\\.[jt]sx?$": [
            "ts-jest",
            {
                diagnostics: {
                    ignoreCodes: [1343],
                },
                astTransformers: {
                    before: [
                        {
                            path: "node_modules/ts-jest-mock-import-meta", // or, alternatively, 'ts-jest-mock-import-meta' directly, without node_modules.
                            options: { metaObjectReplacement: { url: "https://www.url.com" } },
                        },
                    ],
                },
            },
        ],
    },
};
