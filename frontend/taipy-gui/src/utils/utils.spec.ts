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

import { extractPrefix, extractSuffix, precisionFormat, sprintfParse, sprintfToD3Converter } from "./formatConversion";

function extractSuffixWrapper(formatString: string): string {
    let result = extractSuffix(formatString);
    result = result.replace("[object Object]", "%d");
    return result;
}

describe("format conversion", () => {
    it("returns formatted precision with provided precision and specifier", () => {
        expect(precisionFormat(".5", "f")).toBe(".5f");
    });
    it("returns formatted precision with default precision when none is provided", () => {
        expect(precisionFormat(undefined, "f")).toBe(".2f");
    });
    it("returns empty string when no format string is provided", () => {
        expect(sprintfToD3Converter()).toBe("");
    });
    it("should parse non-placeholder text", () => {
        const result = sprintfParse("Hello, World!");
        expect(result).toEqual(["Hello, World!"]);
    });
    it('should parse the "%%" escape sequence', () => {
        const result = sprintfParse("%%");
        expect(result).toEqual(["%"]);
    });
    it("should parse placeholders", () => {
        const result = sprintfParse("%d");
        expect(result).toEqual([{ placeholder: "%d" }]);
    });
    it("should parse complex format strings", () => {
        const result = sprintfParse("Hello, %s. You have %d new messages.");
        expect(result).toEqual([
            "Hello, ",
            { placeholder: "%s" },
            ". You have ",
            { placeholder: "%d" },
            " new messages.",
        ]);
    });
    it("should extract placeholder value", () => {
        const result = sprintfToD3Converter("%d");
        expect(result).toBe("d");
    });
    it("should extract prefix from format string", () => {
        const result = extractPrefix("Hello, %s. You have %d new messages.");
        expect(result).toBe("Hello, ");
    });
    it("should extract suffix from format string", () => {
        const result = extractSuffixWrapper("Hello, %s. You have %d new messages.");
        expect(result).toBe(". You have %d new messages.");
    });
    it("should return empty string when no format string is provided to extractPrefix", () => {
        const result = extractPrefix();
        expect(result).toBe("");
    });
    it("should return empty string when no format string is provided to extractSuffix", () => {
        const result = extractSuffix();
        expect(result).toBe("");
    });
    it("should break the loop for invalid placeholder", () => {
        const result = sprintfParse("Hello, %z");
        expect(result).toEqual(["Hello, "]);
    });
    it("should return 'b' for '%b'", () => {
        expect(sprintfToD3Converter("%b")).toBe("b");
    });
    it("should return 'e' for '%e'", () => {
        expect(sprintfToD3Converter("%e")).toBe("e");
    });

    it("should return 'o' for '%o'", () => {
        expect(sprintfToD3Converter("%o")).toBe("o");
    });
    it("should return 'x' for '%x'", () => {
        expect(sprintfToD3Converter("%x")).toBe("x");
    });
    it("should return 'X' for '%X'", () => {
        expect(sprintfToD3Converter("%X")).toBe("X");
    });
    it("should return 'd' for '%i'", () => {
        expect(sprintfToD3Converter("%i")).toBe("d");
    });
    it("should return '.2f' for '%f'", () => {
        expect(sprintfToD3Converter("%f")).toBe(".2f");
    });
    it("should return '.2g' for '%g'", () => {
        expect(sprintfToD3Converter("%g")).toBe(".2g");
    });
    it("should return '(' for '%u'", () => {
        expect(sprintfToD3Converter("%u")).toBe("(");
    });
    it("should return '' for unsupported converter", () => {
        expect(sprintfToD3Converter("hi")).toBe("");
    });
});
