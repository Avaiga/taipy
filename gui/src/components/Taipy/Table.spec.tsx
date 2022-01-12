import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";

import Table from "./Table";

const tableColumns = JSON.stringify({"Entity": {"dfid": "Entity"}});

describe("Table Component", () => {
    it("renders paginated", async () => {
        const { getByText } = render(<Table data={undefined} columns={tableColumns}  />);
        const elt = getByText("Entity");
        expect(elt.tagName).toBe("DIV");
    });
    it("renders auto loading", async () => {
        const { getByText } = render(<Table data={undefined} columns={tableColumns} autoLoading={true} />);
        const elt = getByText("Entity");
        expect(elt.tagName).toBe("DIV");
    });
});
