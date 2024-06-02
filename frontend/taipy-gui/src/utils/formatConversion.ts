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
 * Regular expressions used for parsing sprintf format strings.
 */
const re = {
    text: /^[^\x25]+/,                         // Matches non-placeholder text
    modulo: /^\x25{2}/,                        // Matches the '%%' escape sequence
    placeholder: /^\x25?(?:\.(\d+))?([b-giostuvxX])/, // Matches placeholders
};

const precisionFormat = (precision?: string, specifier?: string): string => {
    // Default to precision of 2 if not specified
    return "." + (precision?.slice(1) ?? "2") + specifier;
}

const sprintfParse = (fmt?: string): (string | { placeholder: string; })[] => {
    let _fmt = fmt;
    let match;
    const parse_tree = [];

    while (_fmt) {
        if ((match = re.text.exec(_fmt)) !== null) {
            // Non-placeholder text
            parse_tree.push(match[0]);
        } else if ((match = re.modulo.exec(_fmt)) !== null) {
            // '%%' escape sequence
            parse_tree.push('%');
        } else if ((match = re.placeholder.exec(_fmt)) !== null) {
            // Placeholder
            if (match && match[0]) {
                parse_tree.push({
                    placeholder: match[0],
                });
            }
        }

        if (match) {
            _fmt = _fmt.substring(match[0].length);
        }
    }

    return parse_tree;
}

export const sprintfToD3Converter = (fmt?: string): string => {
    const sprintf_fmt_arr = sprintfParse(fmt);
    const objectIndex = sprintf_fmt_arr.findIndex((element) => typeof element === 'object');
    let placeholderValue;

    if (typeof sprintf_fmt_arr[objectIndex] === 'object' && sprintf_fmt_arr[objectIndex] !== null) {
        placeholderValue = (sprintf_fmt_arr[objectIndex] as { placeholder: string }).placeholder;
    }

    if (placeholderValue === undefined) {
        return "";
    }

    return placeholderValue.replace(/%([0-9]*)([.][0-9]+)?([bdieufgoxX])/g, (match, width, precision, type) => {
        switch (type) {
            case "b":
            case "d":
            case "e":
            case "o":
            case "x":
            case "X":
                return type;
            case "i":
                return "d";
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

export const extractPrefix = (fmt?: string): string => {
    const sprintf_fmt_arr = sprintfParse(fmt);
    const objectIndex = sprintf_fmt_arr.findIndex((element) => typeof element === 'object');
    return sprintf_fmt_arr.slice(0, objectIndex).join('');
}

export const extractSuffix = (fmt?: string): string => {
    const sprintf_fmt_arr = sprintfParse(fmt);
    const objectIndex = sprintf_fmt_arr.findIndex((element) => typeof element === 'object');
    return sprintf_fmt_arr.slice(objectIndex + 1).join('');
}
