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

import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";

import Table from "./Table";

const tableColumns = JSON.stringify({"Entity": {"dfid": "Entity"}});

describe("Table Component", () => {
    it("renders paginated", async () => {
        const { getByText } = render(<Table data={undefined} defaultColumns={tableColumns}  />);
        const elt = getByText("Entity");
        expect(elt.tagName).toBe("DIV");
    });
    it("renders auto loading", async () => {
        const { getByText } = render(<Table data={undefined} defaultColumns={tableColumns} autoLoading={true} />);
        const elt = getByText("Entity");
        expect(elt.tagName).toBe("DIV");
    });
});
