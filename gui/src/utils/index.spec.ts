/*
 * Copyright 2023 Avaiga Private Limited
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

import { getNumberString } from "./index";

let myWarn: jest.Mock;

beforeEach(() => {
    myWarn = jest.fn();
    console.warn = myWarn;
})

const getFormatConfig = (numberFormat?: string): FormatConfig => ({timeZone: "", date: "", dateTime: "", number: numberFormat || "", forceTZ: false})

describe("getNumberString", () => {
    it("returns straight", async () => {
        expect(getNumberString(1, undefined, getFormatConfig())).toBe("1");
    });
    it("returns formatted", async () => {
        expect(getNumberString(1, "%.1f", getFormatConfig())).toBe("1.0");
    });
    it("returns formatted float", async () => {
        expect(getNumberString(1.0, "%.0f", getFormatConfig())).toBe("1");
    });
    it("returns default formatted", async () => {
        expect(getNumberString(1, "", getFormatConfig("%.1f"))).toBe("1.0");
    });
    it("returns for non variable format", async () => {
        expect(getNumberString(1, "toto", getFormatConfig())).toBe("toto");
    });
    it("returns formatted over default", async () => {
        expect(getNumberString(1, "%.2f", getFormatConfig("%.1f"))).toBe("1.00");
    });
    it("returns for string", async () => {
        expect(getNumberString("null" as unknown as number, "", getFormatConfig("%.1f"))).toBe("null");
        expect(myWarn).toHaveBeenCalledWith("getNumberString: [sprintf] expecting number but found string")
    });
    it("returns for object", async () => {
        expect(getNumberString({t: 1} as unknown as number, "", getFormatConfig("%.1f"))).toBe("");
        expect(myWarn).toHaveBeenCalledWith("getNumberString: [sprintf] expecting number but found object")
    });
    it("returns for bad format", async () => {
        expect(getNumberString(1, "%.f", getFormatConfig())).toBe("1");
        expect(myWarn).toHaveBeenCalledWith("getNumberString: [sprintf] unexpected placeholder")
    });
    it("returns for null", async () => {
        expect(getNumberString(null as unknown as number, "%2.f", getFormatConfig("%.1f"))).toBe("");
        expect(myWarn).toHaveBeenCalledWith("getNumberString: [sprintf] unexpected placeholder")
    });
    it("returns for undefined", async () => {
        expect(getNumberString(undefined as unknown as number, "%2.f", getFormatConfig("%.1f"))).toBe("");
        expect(myWarn).toHaveBeenCalledWith("getNumberString: [sprintf] unexpected placeholder")
    });
    it("returns for NaN", async () => {
        expect(getNumberString(NaN, "%2.f", getFormatConfig("%.1f"))).toBe("NaN");
        expect(myWarn).toHaveBeenCalledWith("getNumberString: [sprintf] unexpected placeholder")
    });
});
