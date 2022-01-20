import "@testing-library/jest-dom";

import { Column, Float32Vector, Int32Vector, Table } from "apache-arrow";
import { DataFormat, parseData } from "./dataFormat";

const straightData = { data: { key: "value" } };
const extractData = { dataExtraction: true, data: { key: "value" } };
const i32s = Column.new("i32", Int32Vector.from([1, 2, 3]));
const f32s = Column.new("f32", Float32Vector.from([0.1, 0.2, 0.3]));
// Need to find how to make this data a UInt8Array ...
const arrowRecordsData = { format: DataFormat.APACHE_ARROW, orient: "records", data: Table.new(i32s, f32s) };
const arrowListData = { format: DataFormat.APACHE_ARROW, orient: "list", data: Table.new(i32s, f32s) };

describe("does nothing", () => {
    it("returns straight", async () => {
        expect(parseData(straightData)).toBe(straightData);
    });
    it("returns with data extraction", async () => {
        expect(parseData(extractData)).toBe(extractData.data);
    });
    it("returns records from arrow", async () => {
        expect(parseData(arrowRecordsData)).toStrictEqual({ data: [], format: "ARROW", orient: "records" });
    });
    it("returns list from arrow", async () => {
        expect(parseData(arrowListData)).toStrictEqual({ data: {}, format: "ARROW", orient: "list" });
    });
});
