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

const FORMAT_REPLACE_REGEX = /%([0-9]*)([.][0-9]+)?([bdieufgosxX])/g;

/**
 * Converts a sprintf format string to a D3 format string.
 *
 * This function takes a sprintf format string as input and returns a D3 format string.
 * The conversion is done by replacing each sprintf format specifier with the corresponding D3 format specifier.
 * If the input format string is undefined, the function returns undefined.
 * If an error occurs during the conversion, the function logs the error to the console and returns undefined.
 *
 * @param format - The sprintf format string to convert.
 * @returns The converted D3 format string, or undefined if the input is undefined or if an error occurs.
 */
const sprintfToD3Converter = (format: string) => {
    try {
        return format?.replace(FORMAT_REPLACE_REGEX, (match, width, precision, type) => {
            switch (type) {
                case "b":
                    return "b";
                case "d":
                    return "d";
                case "i":
                    return "d";
                case "e":
                    return "e";
                case "f":
                    return "." + (precision?.slice(1) ?? "2") + "f";
                case "g":
                    return "." + (precision?.slice(1) ?? "2") + "g";
                case "o":
                    return "o";
                case "s":
                    return "";
                case "x":
                    return "x";
                case "X":
                    return "X";
                default:
                    return "";
            }
        });
    } catch (error) {
        console.error(`Failed to convert format "${format}" to D3 format: ${error}`);
        return undefined;
    }
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

    try {
        const PREFIX_MATCH_REGEX: RegExp = /.*?(?=%)/;
        return format.match(PREFIX_MATCH_REGEX)?.[0] ?? "";
    } catch (error) {
        console.error(`Failed to extract prefix from format "${format}": ${error}`);
        return undefined;
    }
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

    try {
        const SURFIX_MATCH_REGEX: RegExp = /(?<=[bdieufgosxX])./;
        return format.match(SURFIX_MATCH_REGEX)?.[0] ?? "";
    } catch (error) {
        console.error(`Failed to extract suffix from format "${format}": ${error}`);
        return undefined;
    }
}

/**
 * Extracts the format specifier from the input string.
 * The input string is expected to be in sprintf format.
 * The function returns the format specifier (one of 'b', 'd', 'i', 'e', 'f', 'g', 'o', 's', 'x', 'X') if it exists, or undefined otherwise.
 * @param input - The input string in sprintf format.
 * @returns The extracted format specifier, or undefined if no specifier is found or if the input is undefined.
 */
export const extractFormatSpecifier = (input: string | undefined): string | undefined => {
    if (input === undefined) {
        return undefined;
    }

    try {
        const regex: RegExp = /.*%?([bdieufgosxX]).*/g;
        const convertedInput = sprintfToD3Converter(input);
        return convertedInput ? convertedInput.replace(regex, '$1') : undefined;
    } catch (error) {
        console.error(`Failed to extract format specifier from input "${input}": ${error}`);
        return undefined;
    }
}
