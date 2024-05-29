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

/**
 * Convert sprintf-like format string to D3 format string.
 *
 * @param format - The sprintf-like format string.
 * @returns The converted D3 format string or undefined if an error occurs.
 */
const sprintfToD3Converter = (format: string) => {
    /**
     * Helper function to handle precision formatting.
     *
     * @param precision - The precision part of the format string.
     * @param specifier - The type of formatting.
     * @returns The D3 precision format string.
     */
    const precisionFormat = (precision: string | undefined, specifier: string) => {
        // Default to precision of 2 if not specified
        return "." + (precision?.slice(1) ?? "2") + specifier;
    }

        return format?.replace(/%([0-9]*)([.][0-9]+)?([bdieufgoxX])/g, (match, width, precision, type) => {
            console.log(`Match: ${match}, Width: ${width}, Precision: ${precision}, Type: ${type}`)
            switch (type) {
                case "b":
                case "d":
                case "i":
                case "e":
                case "o":
                case "x":
                case "X":
                    return type;
                case "f":
                    return precisionFormat(precision, "f");
                case "g":
                    return precisionFormat(precision, "g");
                case "u":
                    return "("
                default:
                    return "";
            }
        });
}

/**
 * Extracts the prefix from the format string.
 * @param format - The format string.
 * @returns The extracted prefix, or undefined if the format is undefined.
 */
export const extractPrefix = (format: string | undefined): string | undefined => {
    if (format === undefined) {
        return undefined;
    }
        const PREFIX_MATCH_REGEX: RegExp = /.*?(?=%)/;
        return format.match(PREFIX_MATCH_REGEX)?.[0] ?? "";
}

/**
 * Extracts the suffix from the format string.
 * @param format - The format string.
 * @returns The extracted suffix, or undefined if the format is undefined.
 */
export const extractSuffix = (format: string | undefined): string | undefined => {
    if (format === undefined) {
        return undefined;
    }
        const SURFIX_MATCH_REGEX: RegExp = /(?<=[bdieufgsxX])./;
        return format.match(SURFIX_MATCH_REGEX)?.[0] ?? "";
}

/**
 * Extracts the format specifier from the input string.
 * The input string is expected to be in sprintf format.
 * The function returns the format specifier (one of 'b', 'd', 'i', 'e', 'u', 'f', 'g', 'o', 'x', 'X') if it exists, or undefined otherwise.
 * @param input - The input string in sprintf format.
 * @returns The extracted format specifier, or undefined if no specifier is found or if the input is undefined.
 */
export const extractFormatSpecifier = (input: string | undefined): string | undefined => {
    if (input === undefined) {
        return undefined;
    }
        const regex: RegExp = /%.*\.?[bdieufgoxX]/;
        const match = input.match(regex);
        const format = match ? match[0] : undefined;
        return format ? sprintfToD3Converter(format) : undefined;
}
