import "@testing-library/jest-dom";

import { getNumberString } from "./index";

let myInfo: jest.Mock;

beforeEach(() => {
    myInfo = jest.fn();
    console.info = myInfo;
})

describe("getNumberString", () => {
    it("returns straight", async () => {
        expect(getNumberString(1, undefined, { timeZone: "", dateTime: "", number: "" })).toBe("1");
    });
    it("returns formatted", async () => {
        expect(getNumberString(1, "%.1f", { timeZone: "", dateTime: "", number: "" })).toBe("1.0");
    });
    it("returns formatted float", async () => {
        expect(getNumberString(1.0, "%.0f", { timeZone: "", dateTime: "", number: "" })).toBe("1");
    });
    it("returns default formatted", async () => {
        expect(getNumberString(1, "", { timeZone: "", dateTime: "", number: "%.1f" })).toBe("1.0");
    });
    it("returns for non variable format", async () => {
        expect(getNumberString(1, "toto", { timeZone: "", dateTime: "", number: "" })).toBe("toto");
    });
    it("returns formatted over default", async () => {
        expect(getNumberString(1, "%.2f", { timeZone: "", dateTime: "", number: "%.1f" })).toBe("1.00");
    });
    it("returns for string", async () => {
        expect(getNumberString("null" as unknown as number, "", { timeZone: "", dateTime: "", number: "%.1f" })).toBe("null");
        expect(myInfo).toHaveBeenCalledWith("getNumberString: [sprintf] expecting number but found string")
    });
    it("returns for object", async () => {
        expect(getNumberString({t: 1} as unknown as number, "", { timeZone: "", dateTime: "", number: "%.1f" })).toBe("");
        expect(myInfo).toHaveBeenCalledWith("getNumberString: [sprintf] expecting number but found object")
    });
    it("returns for bad format", async () => {
        expect(getNumberString(1, "%.f", { timeZone: "", dateTime: "", number: "" })).toBe("1");
        expect(myInfo).toHaveBeenCalledWith("getNumberString: [sprintf] unexpected placeholder")
    });
    it("returns for null", async () => {
        expect(getNumberString(null as unknown as number, "%2.f", { timeZone: "", dateTime: "", number: "%.1f" })).toBe("");
        expect(myInfo).toHaveBeenCalledWith("getNumberString: [sprintf] unexpected placeholder")
    });
    it("returns for undefined", async () => {
        expect(getNumberString(undefined as unknown as number, "%2.f", { timeZone: "", dateTime: "", number: "%.1f" })).toBe("");
        expect(myInfo).toHaveBeenCalledWith("getNumberString: [sprintf] unexpected placeholder")
    });
    it("returns for NaN", async () => {
        expect(getNumberString(NaN, "%2.f", { timeZone: "", dateTime: "", number: "%.1f" })).toBe("NaN");
        expect(myInfo).toHaveBeenCalledWith("getNumberString: [sprintf] unexpected placeholder")
    });
});
