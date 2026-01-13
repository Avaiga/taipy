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

import React from "react";
import { parseJSX } from "./parser";

describe("JSX Parser", () => {
    it("parse simple HTML", async () => {
        const elements = parseJSX("<div>Hello World</div>");
        expect(elements).not.toBeNull();
        expect(elements).toHaveLength(1);
        expect(elements[0].type).toBe("div");
        expect(elements[0].props.children).toBe("Hello World");
    });
    it("parse no children HTML", async () => {
        const elements = parseJSX("<hr/>");
        expect(elements).not.toBeNull();
        expect(elements).toHaveLength(1);
        expect(elements[0].type).toBe("hr");
        expect(elements[0].props.children).toBeUndefined();
    });
    it("parse simple jsx", async () => {
        const elements = parseJSX("<MyComponent>Hello World</MyComponent>");
        expect(elements).not.toBeNull();
        expect(elements).toHaveLength(1);
        expect(elements[0].type).toBe("MyComponent");
        expect(elements[0].props.children).toBe("Hello World");
    });
    it("parse complex jsx", async () => {
        const elements = parseJSX("<MyComponent>Hello World<AnotherComponent/></MyComponent><div>Bye</div>");
        expect(elements).not.toBeNull();
        expect(elements).toHaveLength(2);
        expect(elements[0].type).toBe("MyComponent");
        expect(elements[0].props.children).toHaveLength(2);
        const children = elements[0].props.children as React.ReactNode[];
        expect(children[0]).toBe("Hello World");
        expect((children[1] as React.ReactElement).type).toBe("AnotherComponent");
        expect(elements[1].type).toBe("div");
        expect(elements[1].props.children).toBe("Bye");
    });
    it("parse jsx with component", async () => {
        const elements = parseJSX('<MyComponent prop="property">Hello World</MyComponent>', {}, { MyComponent: (props: any) => React.createElement("div", {}) });
        expect(elements).not.toBeNull();
        expect(elements).toHaveLength(1);
        expect(elements[0]).not.toBeNull();
    });
    it("parse jsx with property", async () => {
        const elements = parseJSX('<MyComponent prop="property">Hello World</MyComponent>');
        expect(elements).not.toBeNull();
        expect(elements).toHaveLength(1);
        expect(elements[0].type).toBe("MyComponent");
        expect(elements[0].props.children).toBe("Hello World");
        expect((elements[0].props as any).prop).toBe("property");
    });
    it("parse jsx with property and undefined interpolation", async () => {
        const elements = parseJSX('<MyComponent prop="{!property!}">Hello World</MyComponent>');
        expect(elements).not.toBeNull();
        expect(elements).toHaveLength(1);
        expect(elements[0].type).toBe("MyComponent");
        expect(elements[0].props.children).toBe("Hello World");
        expect((elements[0].props as any).prop).toBeUndefined();
    });
    it("parse jsx with property and interpolation", async () => {
        const state = { property: "prop", objectProp: { subProp: "subProperty" }, numProp: 1, boolProp: true };
        const elements = parseJSX(
            '<MyComponent prop="{!property!}" objectProp="{!objectProp!}" numProp="{!numProp!}" numProp2="{!-100.1!}" boolProp="{!boolProp!}" boolProp2="{!false!}">Hello World</MyComponent>',
            state
        );
        expect(elements).not.toBeNull();
        expect(elements).toHaveLength(1);
        expect(elements[0].type).toBe("MyComponent");
        expect(elements[0].props.children).toBe("Hello World");
        expect((elements[0].props as any).prop).toBe("prop");
        expect((elements[0].props as any).objectProp).toStrictEqual(state.objectProp);
        expect((elements[0].props as any).numProp).toBe(1);
        expect((elements[0].props as any).boolProp).toBe(true);
        expect((elements[0].props as any).noProp).toBeUndefined();
        expect((elements[0].props as any).boolProp2).toBe(false);
        expect((elements[0].props as any).numProp2).toBe(-100.1);
    });
});
