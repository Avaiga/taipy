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

import { tableFromArrays, tableToIPC } from "apache-arrow";
import { DataFormat, parseData } from "./dataFormat";

const straightData = { data: { key: "value" } };
const extractData = { dataExtraction: true, format: "", data: { key: "value" } };
const ipcTable = tableToIPC(tableFromArrays({i32 : new Int32Array([1, 2, 3]), str: ["One", "Two", "Three"]}))

const arrowRecordsData = { format: DataFormat.APACHE_ARROW, orient: "records", data: ipcTable };
const arrowListData = { format: DataFormat.APACHE_ARROW, orient: "list", data: ipcTable };

describe("does nothing", () => {
    it("returns straight", async () => {
        expect(await parseData(straightData)).toBe(straightData);
    });
    it("returns with data extraction", async () => {
        expect(await parseData(extractData)).toBe(extractData.data);
    });
    it("returns records from arrow", async () => {
        expect(await parseData(arrowRecordsData)).toStrictEqual({ data: [{i32: 1, str: "One"}, {i32: 2, str: "Two"}, {i32: 3, str: "Three"}], format: "ARROW", orient: "records" });
    });
    it("returns list from arrow", async () => {
        expect(await parseData(arrowListData)).toStrictEqual({ data: {i32: [1, 2, 3], str: ["One", "Two", "Three"]}, format: "ARROW", orient: "list" });
    });
});
