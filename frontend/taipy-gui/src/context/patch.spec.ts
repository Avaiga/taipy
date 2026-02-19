/*
 * Copyright 2021-2025 Avaiga Private Limited
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
import { patchValue } from "./patch";

describe("patchValue", () => {
    describe("change", () => {
        it("should update the value at the specified path", () => {
            const obj = { a: { b: { c: 1 } } };
            const newObj = patchValue(obj, { a: { b: { c: 2 } } });
            expect(newObj.a.b.c).toBe(2);
        });

        it("should create nested objects if they don't exist", () => {
            const obj = {};
            const patchObj = { a: { b: { c: 1 } } };
            const newObj = patchValue(obj, patchObj);
            expect(JSON.stringify(newObj)).toBe(JSON.stringify(patchObj));
        });

        it("should handle array indices", () => {
            const obj = { a: { b: [1, 2, 3] } };
            const newObj = patchValue(obj, { a: { b: { 1: 4 } } });
            expect(newObj.a.b[1]).toBe(4);
        });

        it("should replace array", () => {
            const obj = { a: { b: [1, 2, 3] } };
            const newObj = patchValue(obj, { a: { b: [0] as unknown as number } });
            expect(newObj.a.b.length).toBe(1);
            expect(newObj.a.b[0]).toBe(0);
        });

        it("should update array", () => {
            const obj = { a: { b: [1, 2, 3] } };
            const newObj = patchValue(obj, { a: { b: { 2: [-1, -2] as unknown as number } } });
            expect(newObj.a.b.length).toBe(4);
            expect(newObj.a.b[0]).toBe(1);
            expect(newObj.a.b[1]).toBe(2);
            expect(newObj.a.b[2]).toBe(-1);
            expect(newObj.a.b[3]).toBe(-2);
        });

        it("should update object in array", () => {
            const obj = { a: { b: [{ c: 1 }, { c: 2 }, { c: 3 }] } };
            const newObj = patchValue(obj, { a: { b: { 2: { c: -1 } } } });
            expect(newObj.a.b.length).toBe(3);
            expect(newObj.a.b[0].c).toBe(1);
            expect(newObj.a.b[2].c).toBe(-1);
        });

        it("should update an array of objects", () => {
            const obj = { a: { b: [{ c: 1 }, { c: 2, d: 3 }, { c: 4 }] } };
            const newObj = patchValue(obj, { a: { b: { 1: [{ c: -1 }] as unknown as number } } });
            expect(newObj.a.b[1].c).toBe(-1);
            expect(newObj.a.b[1].d).toBe(3);
        });

        it("should create nested arrays if they don't exist", () => {
            const obj = {};
            const patchObj = { a: { b: { 0: 1 } } };
            const newObj = patchValue(obj, patchObj);
            expect(JSON.stringify(newObj)).toBe(JSON.stringify(patchObj));
        });

        it("should not modify the original object if the value is the same", () => {
            const obj = { a: { b: { c: 1 } } };
            const originalObj = JSON.stringify(obj);
            const newObj = patchValue(obj, { a: { b: { c: 1 } } });
            expect(JSON.stringify(newObj)).toBe(originalObj);
        });

        it("should insert in an array if index < 0", () => {
            const obj = { a: { b: [0, 1, 2] } };
            const newObj = patchValue(obj, { a: { b: { "-1": [3] as unknown as number } } });
            expect(newObj.a.b[0]).toBe(3);
            expect(newObj.a.b[1]).toBe(0);
            expect(newObj.a.b.length).toBe(4);

            const newObj2 = patchValue(obj, { a: { b: { "-3": [3] as unknown as number } } });
            expect(newObj2.a.b[2]).toBe(3);
            expect(newObj2.a.b[3]).toBe(2);
            expect(newObj2.a.b.length).toBe(4);
        });

        it("should update an empty array", () => {
            const obj = { a: { b: [] } };
            const newObj = patchValue(obj, { a: { b: { 0: 1 as unknown as number } } });
            expect(newObj.a.b[0]).toBe(1);
            expect(newObj.a.b.length).toBe(1);

            const newObj2 = patchValue(obj, { a: { b: { 0: [2, 3] as unknown as number } } });
            expect(newObj2.a.b[0]).toBe(2);
            expect(newObj2.a.b[1]).toBe(3);
            expect(newObj2.a.b.length).toBe(2);

        });

    });
    describe("remove", () => {
        it("should remove the value at the specified path", () => {
            const obj = { a: { b: { c: 1, d: 2 } } };
            const newObj = patchValue(obj, undefined, { a: { b: { c: null } } });
            expect(newObj.a.b.c).toBeUndefined();
            expect(newObj.a.b.d).toBe(2);
        });
        it("should handle array indices", () => {
            const obj = { a: { b: [1, 2, 3] } };
            const newObj = patchValue(obj, undefined, { a: { b: { 1: null } } });
            expect(newObj.a.b.length).toBe(2);
            expect(newObj.a.b[0]).toBe(1);
            expect(newObj.a.b[1]).toBe(3);
        });
        it("should not modify the original object if the path does not exist", () => {
            const obj = { a: { b: { c: 1 } } };
            const newObj = patchValue(obj, undefined, { a: { b: { d: null } } });
            expect(newObj).toStrictEqual(obj);
        });
        it("should modify the original object if the value to remove is not null", () => {
            const obj = { a: { b: { c: 1, d: 2 } } };
            const newObj = patchValue(obj, undefined, { a: { b: { c: 2 as unknown as null } } });
            expect(newObj.a.b.c).toBeUndefined;
            expect(newObj.a.b.c).toBeUndefined;
            expect(newObj.a.b.d).toBe(2);
        });
    });
});
