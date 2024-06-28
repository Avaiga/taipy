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

import "@testing-library/jest-dom";
import { FormatConfig } from "../context/taipyReducers";

import { getNumberString, getDateTimeString } from "./index";

let myWarn: jest.Mock;

beforeEach(() => {
    myWarn = jest.fn();
    console.warn = myWarn;
})

const getNumberFormatConfig = (numberFormat?: string): FormatConfig => ({timeZone: "", date: "", dateTime: "", number: numberFormat || "", forceTZ: false})
const getDateFormatConfig = (dateFormat?: string): FormatConfig => ({timeZone: "", date: dateFormat || "", dateTime: dateFormat || "", number: "", forceTZ: false})

describe("getNumberString", () => {
    it("returns straight", async () => {
        expect(getNumberString(1, undefined, getNumberFormatConfig())).toBe("1");
    });
    it("returns formatted", async () => {
        expect(getNumberString(1, "%.1f", getNumberFormatConfig())).toBe("1.0");
    });
    it("returns formatted float", async () => {
        expect(getNumberString(1.0, "%.0f", getNumberFormatConfig())).toBe("1");
    });
    it("returns default formatted", async () => {
        expect(getNumberString(1, "", getNumberFormatConfig("%.1f"))).toBe("1.0");
    });
    it("returns for non variable format", async () => {
        expect(getNumberString(1, "toto", getNumberFormatConfig())).toBe("toto");
    });
    it("returns formatted over default", async () => {
        expect(getNumberString(1, "%.2f", getNumberFormatConfig("%.1f"))).toBe("1.00");
    });
    it("returns for string", async () => {
        expect(getNumberString("null" as unknown as number, "", getNumberFormatConfig("%.1f"))).toBe("null");
        expect(myWarn).toHaveBeenCalledWith("Invalid number format:", "[sprintf] expecting number but found string")
    });
    it("returns for object", async () => {
        expect(getNumberString({t: 1} as unknown as number, "", getNumberFormatConfig("%.1f"))).toBe("");
        expect(myWarn).toHaveBeenCalledWith("Invalid number format:", "[sprintf] expecting number but found object")
    });
    it("returns for bad format", async () => {
        expect(getNumberString(1, "%.f", getNumberFormatConfig())).toBe("1");
        expect(myWarn).toHaveBeenCalledWith("Invalid number format:", "[sprintf] unexpected placeholder")
    });
    it("returns for null", async () => {
        expect(getNumberString(null as unknown as number, "%2.f", getNumberFormatConfig("%.1f"))).toBe("");
        expect(myWarn).toHaveBeenCalledWith("Invalid number format:", "[sprintf] unexpected placeholder")
    });
    it("returns for undefined", async () => {
        expect(getNumberString(undefined as unknown as number, "%2.f", getNumberFormatConfig("%.1f"))).toBe("");
        expect(myWarn).toHaveBeenCalledWith("Invalid number format:", "[sprintf] unexpected placeholder")
    });
    it("returns for NaN", async () => {
        expect(getNumberString(NaN, "%2.f", getNumberFormatConfig("%.1f"))).toBe("NaN");
        expect(myWarn).toHaveBeenCalledWith("Invalid number format:", "[sprintf] unexpected placeholder")
    });
});

describe("getDateTimeString", () => {
    it("returns straight", async () => {
        expect(getDateTimeString("2024-10-05", undefined, getDateFormatConfig())).toContain("05 2024");
    });
    it("returns formatted", async () => {
        expect(getDateTimeString("2024-10-05", "dd-MM-yy", getDateFormatConfig())).toBe("05-10-24");
    });
    it("returns default formatted", async () => {
        expect(getDateTimeString("2024-10-05", "", getDateFormatConfig("dd-MM-yy"))).toBe("05-10-24");
    });
    it("returns formatted over default", async () => {
        expect(getDateTimeString("2024-10-05", "dd-MM-yy", getNumberFormatConfig("yy-MM-dd"))).toBe("05-10-24");
    });
    it("returns for string", async () => {
        expect(getDateTimeString("null" as unknown as string, "", getDateFormatConfig("dd-MM-yy"))).toBe("Invalid Date");
        expect(myWarn).toHaveBeenCalledWith("Invalid date format:", "Invalid time value")
    });
    it("returns for object", async () => {
        expect(getDateTimeString({t: 1} as unknown as string, "", getDateFormatConfig("dd-MM-yy"))).toBe("Invalid Date");
        expect(myWarn).toHaveBeenCalledWith("Invalid date format:", "Invalid time value")
    });
    it("returns for bad format", async () => {
        expect(getDateTimeString("2024-10-05", "ABCDEF", getDateFormatConfig())).toContain("05 2024");
        expect(myWarn).toHaveBeenCalled()
        expect(myWarn.mock.lastCall).toHaveLength(2)
        expect(myWarn.mock.lastCall[0]).toBe("Invalid date format:")
        expect(myWarn.mock.lastCall[1]).toContain("Format string contains an unescaped latin alphabet character `A`")
    });
    it("returns for null", async () => {
        expect(getDateTimeString(null as unknown as string, "dd-MM-yy", getDateFormatConfig())).toBe("null");
        expect(myWarn).toHaveBeenCalledWith("Invalid date format:", "Invalid time value")
    });
    it("returns for undefined", async () => {
        expect(getDateTimeString(undefined as unknown as string, "dd-MM-yy", getDateFormatConfig())).toBe("null");
        expect(myWarn).toHaveBeenCalledWith("Invalid date format:", "Invalid time value")
    });
});
